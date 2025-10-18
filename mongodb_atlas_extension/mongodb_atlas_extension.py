"""
MongoDB Atlas Connection Monitoring Extension for Dynatrace
Collects authentication and connection metrics from MongoDB Atlas logs
"""

import requests
from requests.auth import HTTPDigestAuth
import gzip
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
from dynatrace_extension import Extension, Status, StatusValue


class MongoDBAtlasExtension(Extension):
    """MongoDB Atlas monitoring extension"""
    
    def initialize(self):
        """Initialize extension with configuration"""
        import os
        
        # Primeiro: tentar via activation_config (produção)
        self.public_key = str(self.activation_config.get("public_key") or "").strip()
        self.private_key = str(self.activation_config.get("private_key") or "").strip()
        self.group_id = str(self.activation_config.get("group_id") or "").strip()
        self.cluster_name = str(self.activation_config.get("cluster_name") or "mongodb-atlas").strip()
        
        hours_ago_val = self.activation_config.get("hours_ago")
        self.hours_ago = int(hours_ago_val) if hours_ago_val is not None else 4
        
        minutes_window_val = self.activation_config.get("minutes_window")
        self.minutes_window = int(minutes_window_val) if minutes_window_val is not None else 6
        
        execution_interval_val = self.activation_config.get("execution_interval_minutes")
        self.execution_interval_minutes = int(execution_interval_val) if execution_interval_val is not None else 5
        
        # Fallback: se public_key estiver vazio, tentar arquivo local com secrets
        if not self.public_key:
            self.logger.info("Config not found via activation_config, trying local files...")
            
            config = self._load_local_config_with_secrets()
            
            if config:
                self.public_key = str(config.get("public_key") or "").strip()
                self.private_key = str(config.get("private_key") or "").strip()
                self.group_id = str(config.get("group_id") or "").strip()
                self.cluster_name = str(config.get("cluster_name") or "clarobr-mongoprd-nfcomiti-saeast1").strip()
                
                try:
                    self.hours_ago = int(config.get("hours_ago", 4))
                except (TypeError, ValueError):
                    self.hours_ago = 4
                
                try:
                    self.minutes_window = int(config.get("minutes_window", 6))
                except (TypeError, ValueError):
                    self.minutes_window = 6
                
                try:
                    self.execution_interval_minutes = int(config.get("execution_interval_minutes", 5))
                except (TypeError, ValueError):
                    self.execution_interval_minutes = 5
                
                self.logger.info("Configuration loaded from local files with secrets")
        
        self.logger.info(f"Configuration loaded - Cluster: {self.cluster_name}, Group: {self.group_id}")
        
        # Validate required fields
        if not self.public_key:
            raise ValueError(
                "public_key is required. "
                "In production: configure via Dynatrace UI. "
                "For local testing: create activation.json and secrets.json"
            )
        if not self.private_key:
            raise ValueError("private_key is required in configuration")
        if not self.group_id:
            raise ValueError("group_id is required in configuration")
        
        self.base_url = "https://cloud.mongodb.com/api/atlas/v2"
        self.headers = {
            "Accept": "application/vnd.atlas.2023-02-01+json",
            "Content-Type": "application/json"
        }
        
        self.base_dimensions = {
            "cluster": self.cluster_name,
            "group_id": self.group_id
        }
        
        self.logger.info(f"MongoDB Atlas Extension initialized for cluster: {self.cluster_name}")
    
    def _load_local_config_with_secrets(self):
        """Load activation.json and substitute secrets from secrets.json"""
        import os
        
        possible_paths = [
            ('activation.json', 'secrets.json'),
            (os.path.join(os.getcwd(), 'activation.json'), os.path.join(os.getcwd(), 'secrets.json')),
            (os.path.join(os.path.dirname(__file__), 'activation.json'), os.path.join(os.path.dirname(__file__), 'secrets.json')),
        ]
        
        for activation_path, secrets_path in possible_paths:
            if os.path.exists(activation_path):
                self.logger.info(f"Found activation.json at: {activation_path}")
                try:
                    # Ler activation.json
                    with open(activation_path, 'r') as f:
                        activation_content = f.read()
                    
                    # Ler secrets.json se existir
                    secrets = {}
                    if os.path.exists(secrets_path):
                        self.logger.info(f"Found secrets.json at: {secrets_path}")
                        with open(secrets_path, 'r') as f:
                            secrets = json.load(f)
                    
                    # Substituir {{key}} pelos valores de secrets
                    def replace_secret(match):
                        key = match.group(1)
                        if key in secrets:
                            return secrets[key]
                        else:
                            self.logger.warning(f"Secret key '{key}' not found in secrets.json")
                            return match.group(0)  # Retorna o original se não encontrar
                    
                    # Substituir todos os {{key}} no conteúdo
                    substituted_content = re.sub(r'\{\{([^}]+)\}\}', replace_secret, activation_content)
                    
                    # Parse JSON depois da substituição
                    config = json.loads(substituted_content)
                    
                    self.logger.info(f"Config loaded and secrets substituted. Keys: {list(config.keys())}")
                    return config
                    
                except Exception as e:
                    self.logger.error(f"Error loading config: {e}")
                    return None
        
        self.logger.error("No activation.json found")
        return None
    
    def query(self):
        """Método query() - Chama collect_metrics()"""
        return self.collect_metrics()
    
    def collect_metrics(self):
        """Coleta métricas do MongoDB Atlas"""
        try:
            processes = self._get_processes()
            if not processes:
                self.logger.warning("No processes found")
                return Status(StatusValue.OK)
            
            all_events = []
            for process in processes:
                hostname = process.get('hostname')
                if not hostname:
                    continue
                
                self.logger.info(f"Collecting logs from: {hostname}")
                logs = self._get_process_logs(hostname)
                
                if logs:
                    events = self._parse_connection_logs(logs)
                    # ADICIONAR hostname a cada evento para usar como dimensão "node"
                    for event in events:
                        event['node'] = hostname
                    self.logger.info(f"Found {len(events)} events from {hostname}")
                    all_events.extend(events)
            
            if not all_events:
                self.logger.warning("No events found in logs")
                return Status(StatusValue.OK)
            
            self._process_and_send_metrics(all_events)
            
            return Status(StatusValue.OK)
            
        except Exception as e:
            self.logger.error(f"Error in query: {str(e)}", exc_info=True)
            return Status(StatusValue.GENERIC_ERROR, f"Query failed: {str(e)}")
    
    def _get_processes(self):
        """Get list of MongoDB processes"""
        url = f"{self.base_url}/groups/{self.group_id}/processes"
        
        try:
            response = requests.get(
                url,
                auth=HTTPDigestAuth(self.public_key, self.private_key),
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                self.logger.error(f"Failed to get processes: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting processes: {str(e)}")
            return None
    
    def _get_process_logs(self, hostname):
        """Download logs from a specific hostname"""
        url = f"{self.base_url}/groups/{self.group_id}/clusters/{hostname}/logs/mongodb.gz"
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=self.hours_ago)
        
        params = {
            "startDate": int(start_time.timestamp()),
            "endDate": int(end_time.timestamp())
        }
        
        log_headers = {
            "Accept": "application/vnd.atlas.2023-02-01+gzip"
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                auth=HTTPDigestAuth(self.public_key, self.private_key),
                headers=log_headers,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.content
                if len(content) == 0:
                    return None
                
                decompressed = gzip.decompress(content).decode('utf-8')
                return decompressed
            else:
                self.logger.warning(f"Failed to get logs from {hostname}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting logs from {hostname}: {str(e)}")
            return None
    
    def _parse_connection_logs(self, log_content):
        """Parse logs and extract connection/authentication events"""
        connection_events = []
        
        connection_log_ids = {
            22943: "Connection accepted",
            22944: "Connection ended",
            20003: "Authentication failed",
            20250: "Successfully authenticated",
        }
        
        for line in log_content.split('\n'):
            if not line.strip():
                continue
                
            try:
                log_entry = json.loads(line)
                log_id = log_entry.get('id')
                component = log_entry.get('c', '')
                msg = log_entry.get('msg', '')
                
                is_target_event = (
                    log_id in connection_log_ids or
                    component in ['ACCESS'] or
                    any(kw in msg.lower() for kw in ['authentication', 'authenticated'])
                )
                
                if is_target_event:
                    log_entry['event_type'] = connection_log_ids.get(log_id, msg if msg else "Unknown")
                    connection_events.append(log_entry)
                    
            except json.JSONDecodeError:
                continue
        
        return connection_events
    
    def _extract_ip_without_port(self, address):
        """Remove port from IP address"""
        if not address or not isinstance(address, str):
            return address
        if ':' in address:
            return address.split(':')[0]
        return address
    
    def _safe_str(self, value):
        """Convert value to string safely"""
        if isinstance(value, dict):
            if 'user' in value:
                return str(value['user'])
            return json.dumps(value, default=str, ensure_ascii=False)
        elif isinstance(value, list):
            return json.dumps(value, default=str, ensure_ascii=False)
        return str(value)
    
    def _process_and_send_metrics(self, connections):
        """Process events and send metrics to Dynatrace"""
        
        timestamps = []
        for evento in connections:
            ts_str = evento.get('t', {}).get('$date')
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    timestamps.append(ts)
                except:
                    continue
        
        if not timestamps:
            self.logger.warning("No valid timestamps found")
            return
        
        max_time = max(timestamps)
        ultimo_minuto_completo = max_time.replace(second=0, microsecond=0) - timedelta(minutes=1)
        primeiro_minuto = ultimo_minuto_completo - timedelta(minutes=self.minutes_window-1)
        
        self.logger.info(f"Processing window: {primeiro_minuto} to {ultimo_minuto_completo}")
        
        eventos_por_minuto = defaultdict(lambda: defaultdict(list))
        
        for evento in connections:
            ts_str = evento.get('t', {}).get('$date')
            if not ts_str:
                continue
            
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                minuto = ts.replace(second=0, microsecond=0)
                
                if minuto < primeiro_minuto or minuto > ultimo_minuto_completo:
                    continue
                
                evento_tipo = evento.get('event_type')
                eventos_por_minuto[minuto][evento_tipo].append(evento)
            except:
                continue
        
        minutos_range = []
        current = primeiro_minuto
        while current <= ultimo_minuto_completo:
            minutos_range.append(current)
            current += timedelta(minutes=1)
        
        metrics_count = 0
        
        for minuto in sorted(minutos_range):
            timestamp_epoch = int(minuto.timestamp())
            
            # Successfully authenticated
            auth_ok_eventos = eventos_por_minuto[minuto].get("Successfully authenticated", [])
            
            for evt in auth_ok_eventos:
                attr = evt.get('attr', {})
                
                client_ip = self._extract_ip_without_port(attr.get('client', 'unknown'))
                db = attr.get('db', 'unknown')
                mechanism = attr.get('mechanism', 'unknown')
                user = self._safe_str(attr.get('user', 'unknown'))
                micros = attr.get('metrics', {}).get('conversation_duration', {}).get('micros', 0)
                node = evt.get('node', 'unknown')
                
                auth_dimensions = {
                    "client_ip": client_ip,
                    "database": db,
                    "mechanism": mechanism,
                    "user": user,
                    "node": node,
                    "timestamp": timestamp_epoch,
                    **self.base_dimensions
                }
                
                self.report_metric("mongodb.atlas.auth.success.count", 1, auth_dimensions)
                self.report_metric("mongodb.atlas.auth.success.duration_micros", micros, auth_dimensions)
                metrics_count += 2
            
            # Authentication failed
            auth_fail_eventos = eventos_por_minuto[minuto].get("Authentication failed", [])
            
            if not auth_fail_eventos:
                auth_fail_base_dimensions = {
                    "client_ip": "none",
                    "database": "none",
                    "mechanism": "none",
                    "user": "none",
                    "node": "none",
                    "timestamp": timestamp_epoch,
                    **self.base_dimensions
                }
                
                self.report_metric("mongodb.atlas.auth.failed.count", 0, auth_fail_base_dimensions)
                metrics_count += 1
            else:
                for evt in auth_fail_eventos:
                    attr = evt.get('attr', {})
                    
                    client_ip = self._extract_ip_without_port(attr.get('client', 'unknown'))
                    db = attr.get('db', 'unknown')
                    mechanism = attr.get('mechanism', 'unknown')
                    user = self._safe_str(attr.get('user', 'unknown'))
                    micros = attr.get('metrics', {}).get('conversation_duration', {}).get('micros', 0)
                    node = evt.get('node', 'unknown')
                    
                    auth_fail_dimensions = {
                        "client_ip": client_ip,
                        "database": db,
                        "mechanism": mechanism,
                        "user": user,
                        "node": node,
                        "timestamp": timestamp_epoch,
                        **self.base_dimensions
                    }
                    
                    self.report_metric("mongodb.atlas.auth.failed.count", 1, auth_fail_dimensions)
                    self.report_metric("mongodb.atlas.auth.failed.duration_micros", micros, auth_fail_dimensions)
                    metrics_count += 2
            
            # Connection accepted
            conn_accept_eventos = eventos_por_minuto[minuto].get("Connection accepted", [])
            
            for evt in conn_accept_eventos:
                attr = evt.get('attr', {})
                
                connection_id = attr.get('connectionId', 'unknown')
                is_load_balanced = str(attr.get('isLoadBalanced', False))
                remote_ip = self._extract_ip_without_port(attr.get('remote', 'unknown'))
                node = evt.get('node', 'unknown')
                
                uuid_val = attr.get('uuid', {})
                if isinstance(uuid_val, dict) and 'uuid' in uuid_val:
                    uuid_str = uuid_val['uuid'].get('$uuid', 'unknown')
                else:
                    uuid_str = self._safe_str(uuid_val)
                
                conn_accept_dimensions = {
                    "connection_id": str(connection_id),
                    "is_load_balanced": is_load_balanced,
                    "remote_ip": remote_ip,
                    "uuid": uuid_str,
                    "node": node,
                    "timestamp": timestamp_epoch,
                    **self.base_dimensions
                }
                
                self.report_metric("mongodb.atlas.connection.accepted.count", 1, conn_accept_dimensions)
                metrics_count += 1
            
            # Connection ended
            conn_end_eventos = eventos_por_minuto[minuto].get("Connection ended", [])
            
            for evt in conn_end_eventos:
                attr = evt.get('attr', {})
                
                connection_id = attr.get('connectionId', 'unknown')
                is_load_balanced = str(attr.get('isLoadBalanced', False))
                remote_ip = self._extract_ip_without_port(attr.get('remote', 'unknown'))
                node = evt.get('node', 'unknown')
                
                uuid_val = attr.get('uuid', {})
                if isinstance(uuid_val, dict) and 'uuid' in uuid_val:
                    uuid_str = uuid_val['uuid'].get('$uuid', 'unknown')
                else:
                    uuid_str = self._safe_str(uuid_val)
                
                conn_end_dimensions = {
                    "connection_id": str(connection_id),
                    "is_load_balanced": is_load_balanced,
                    "remote_ip": remote_ip,
                    "uuid": uuid_str,
                    "node": node,
                    "timestamp": timestamp_epoch,
                    **self.base_dimensions
                }
                
                self.report_metric("mongodb.atlas.connection.ended.count", 1, conn_end_dimensions)
                metrics_count += 1
        
        self.logger.info(f"Sent {metrics_count} metrics to Dynatrace")


def main():
    """Entry point for the extension"""
    MongoDBAtlasExtension().run()


if __name__ == '__main__':
    main()