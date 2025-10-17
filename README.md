![MongoDB Atlas Connection Event Extension](icon.png)

# MongoDB Atlas Connection Monitor

Monitors authentication and connection metrics for MongoDB Atlas clusters using the Atlas API.  
Provides insights into connection performance, authentication trends, and overall cluster availability.

---

## 📊 Metrics collected

| Category | Metric | Description |
|-----------|---------|-------------|
| **Authentication** | `mongodb.atlas.auth.success.count` | Number of successful authentication events |
| **Authentication** | `mongodb.atlas.auth.failed.count` | Number of failed authentication events |
| **Connections** | `mongodb.atlas.connection.accepted.count` | Number of accepted connections |
| **Connections** | `mongodb.atlas.connection.ended.count` | Number of ended connections |
| **Performance** | `mongodb.atlas.auth.success.duration_micros` | Duration of successful authentication (µs) |
| **Performance** | `mongodb.atlas.auth.failed.duration_micros` | Duration of failed authentication (µs) |

---

## ⚙️ Configuration

When activating the extension, provide the following parameters:

| Parameter | Type | Description |
|------------|------|-------------|
| **public_key** | text | MongoDB Atlas API public key |
| **private_key** | secret | MongoDB Atlas API private key (encrypted) |
| **group_id** | text | MongoDB Atlas Project / Group ID |
| **cluster_name** | text | Name of the MongoDB Atlas cluster |
| **hours_ago** | integer | Log collection period (hours) |
| **minutes_window** | integer | Metrics window (minutes) |
| **execution_interval_minutes** | integer | How often to collect metrics (minutes) |

---

## 🧠 Deployment notes

- This is a **Python Remote Extension (RPE)**, executed on an **ActiveGate**.  
- Make sure your ActiveGate host has outbound HTTPS access to the MongoDB Atlas API.  
- Use the Dynatrace Extension Execution Controller to monitor execution logs.

---

## 📘 Example dashboard

![MongoDB Atlas Overview](screenshot1.png)

---

## 🧩 Technical details

| Component | Description |
|------------|-------------|
| **Runtime** | Python 3.10+ |
| **SDK** | Dynatrace Extensions SDK 1.0+ |
| **Source module** | `mongodb_atlas_extension` |
| **Activation schema** | `activationSchema.json` |

---

© 2025 Yamana — Custom Dynatrace Extension for MongoDB Atlas Monitoring

