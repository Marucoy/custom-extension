# Get Started

## Prerequisites

Before activating this extension, ensure you have:

### MongoDB Atlas Requirements

1. **MongoDB Atlas Project** with a running cluster
2. **API Keys** with appropriate permissions:
   - Go to MongoDB Atlas → Organization Settings → Access Manager → API Keys
   - Create API Key with **Project Read Only** permission
   - **Important:** Note the Public Key and Private Key (Private Key shown only once!)
3. **Project/Group ID**:
   - Go to your MongoDB Atlas Project → Settings
   - Copy the Project ID (also called Group ID)

### Dynatrace Requirements

- Dynatrace Environment with **ActiveGate** deployed
- **Extension 2.0** capability enabled
- Minimum Dynatrace version: **1.310.0**

## Installation Steps

### 1. Upload Extension
```bash
# Build the extension
dt-sdk build

# Upload to Dynatrace
dt-sdk upload --api-token YOUR_TOKEN --url YOUR_ENV_URL
```

### 2. Configure Extension

1. Go to **Dynatrace → Settings → Monitoring → Monitored Technologies**
2. Find **MongoDB Atlas Connection Monitoring**
3. Click **Add configuration**
4. Fill in the required fields:

| Field | Description | Example |
|-------|-------------|---------|
| **Atlas Public Key** | MongoDB Atlas API Public Key | `foowbuoj` |
| **Atlas Private Key** | MongoDB Atlas API Private Key | `********` |
| **Group ID** | MongoDB Atlas Project/Group ID | `67bf53a9cc3d7b3cc86ab20b` |
| **Cluster Name** | Display name for your cluster | `production-cluster` |
| **Log Collection Period** | Hours of logs to fetch | `4` (default) |
| **Metrics Window** | Minutes to aggregate | `6` (default) |
| **Execution Interval** | Minutes between runs | `5` (default) |

5. Select **Feature Sets** (recommended: all)
6. Click **Save**

### 3. Verify Installation

After 5-10 minutes, check that metrics are arriving:

1. Go to **Metrics → Filter by: mongodb.atlas**
2. You should see metrics like:
   - `mongodb.atlas.auth.success.count`
   - `mongodb.atlas.auth.failed.count`
   - `mongodb.atlas.connection.accepted.count`
   - `mongodb.atlas.connection.ended.count`

## Configuration Options

### Log Collection Period (hours_ago)

**Default:** 4 hours  
**Range:** 1-24 hours  
**Description:** How far back to look for logs in each collection cycle

**Recommendation:** 
- Use 4-6 hours for production (ensures no gaps)
- Use 1-2 hours for testing (faster iterations)

### Metrics Window (minutes_window)

**Default:** 6 minutes  
**Range:** 1-60 minutes  
**Description:** Number of complete minutes to process and report

**Recommendation:**
- Keep at 6 minutes for standard monitoring
- Increase to 10-15 for lower frequency reporting

### Execution Interval (execution_interval_minutes)

**Default:** 5 minutes  
**Range:** 1-60 minutes  
**Description:** How often the extension runs

**Recommendation:**
- 5 minutes for real-time monitoring
- 15-30 minutes for less critical environments

## Troubleshooting

### No metrics appearing

**Check:**
1. ActiveGate logs: `/var/lib/dynatrace/remotepluginmodule/log/extensions/`
2. Extension configuration is saved and enabled
3. MongoDB Atlas API keys have correct permissions
4. API keys are not IP-restricted (or ActiveGate IP is whitelisted)

### Authentication errors

**Error:** `Failed to get processes: 401`  
**Solution:** Verify API keys are correct and have Project Read Only permission

**Error:** `Failed to get processes: 403`  
**Solution:** Whitelist ActiveGate IP in MongoDB Atlas API Key access list

### No logs found

**Error:** `No events found in logs`  
**Solution:** 
- Verify cluster has recent activity
- Check `hours_ago` setting is not too far in the past
- Ensure cluster name is correct

## Next Steps

✅ Create custom **Dashboards** with your metrics  
✅ Set up **Alerts** for failed authentications  
✅ Build **Workflows** for automated responses  
✅ Integrate with **Davis AI** for anomaly detection
