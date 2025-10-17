# MongoDB Atlas Connection Monitoring

Monitor authentication and connection events from MongoDB Atlas logs in real-time.

## Overview

This extension collects and analyzes MongoDB Atlas logs to provide insights into:

- **Authentication Events**: Track successful and failed login attempts
- **Connection Lifecycle**: Monitor connections from acceptance to termination
- **Security Monitoring**: Identify suspicious authentication patterns
- **Performance Metrics**: Measure authentication duration

## Key Metrics

### Authentication Metrics

- `mongodb.atlas.auth.success.count` - Successful authentications
- `mongodb.atlas.auth.success.duration_micros` - Authentication duration (microseconds)
- `mongodb.atlas.auth.failed.count` - Failed authentication attempts
- `mongodb.atlas.auth.failed.duration_micros` - Failed auth attempt duration

### Connection Metrics

- `mongodb.atlas.connection.accepted.count` - New connections accepted
- `mongodb.atlas.connection.ended.count` - Connections terminated

### Dimensions

All metrics include:
- `client_ip` - Client IP address
- `database` - Database name
- `mechanism` - Authentication mechanism (SCRAM-SHA-1, SCRAM-SHA-256, etc.)
- `user` - Username
- `cluster` - Cluster name
- `group_id` - MongoDB Atlas Project/Group ID

## Prerequisites

### MongoDB Atlas

1. **API Keys** with Project Read Only permission
   - Go to: MongoDB Atlas → Organization → Access Manager → API Keys
   - Create new API Key
   - **Save the Private Key** (shown only once!)

2. **Project/Group ID**
   - Go to: MongoDB Atlas → Project → Settings
   - Copy the Project ID

3. **Whitelist ActiveGate IP**
   - Go to: API Key → Access List
   - Add your ActiveGate's public IP address

### Dynatrace

- Dynatrace Environment with ActiveGate deployed
- Minimum version: 1.310.0

## Configuration

1. **Navigate to Settings → Monitoring → Monitored Technologies**
2. Find **MongoDB Atlas Connection Monitoring**
3. Click **Add configuration**
4. Fill in:

| Parameter | Description | Example |
|-----------|-------------|---------|
| Atlas Public Key | MongoDB Atlas API Public Key | `abcdefgh` |
| Atlas Private Key | MongoDB Atlas API Private Key | `********` |
| Group ID | MongoDB Atlas Project/Group ID | `507f1f77bcf86cd799439011` |
| Cluster Name | Display name for the cluster | `production-cluster` |
| Log Collection Period | Hours of logs to fetch each cycle | `4` |
| Metrics Window | Minutes to aggregate metrics | `6` |
| Execution Interval | Minutes between collections | `5` |

5. Select **Feature Sets**: `connection-monitoring` (recommended)
6. Click **Save**

## Use Cases

### Security Monitoring

**Track authentication failures:**
```
mongodb.atlas.auth.failed.count
| filter client_ip != "known_ip"
| alert if count > 10
```

### Performance Analysis

**Monitor authentication duration:**
```
mongodb.atlas.auth.success.duration_micros
| summarize avg by database
```

### Connection Tracking

**Analyze connection patterns:**
```
mongodb.atlas.connection.accepted.count
| compare with mongodb.atlas.connection.ended.count
```

## Troubleshooting

### No metrics appearing

**Check ActiveGate logs:**
```bash
tail -f /var/lib/dynatrace/remotepluginmodule/log/extensions/custom_mongodb.atlas.connection_*.log
```

**Common issues:**
- API keys incorrect → Verify in MongoDB Atlas
- IP not whitelisted → Add ActiveGate IP to API Key access list
- Cluster inactive → Ensure cluster has recent activity

### Authentication errors

**Error 401:** API keys are invalid  
**Error 403:** IP address not whitelisted  
**Error 404:** Cluster name or group ID incorrect

## Support

For issues or questions:
- Check ActiveGate logs for detailed error messages
- Verify MongoDB Atlas API credentials
- Ensure cluster name matches exactly
