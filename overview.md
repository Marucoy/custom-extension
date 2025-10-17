# Overview

The **MongoDB Atlas Connection Monitoring Extension** enables real-time monitoring of authentication and connection events from your MongoDB Atlas clusters through log analysis.

This extension collects and analyzes MongoDB Atlas logs to track:
- **Successful authentications** with duration metrics
- **Failed authentication attempts** for security monitoring
- **Connection accepted** events
- **Connection ended** events

All metrics are broken down by:
- Client IP address
- Database name
- Authentication mechanism (SCRAM-SHA-1, SCRAM-SHA-256, etc.)
- Username
- Connection details (UUID, load balancing status)

## Key Features

✅ **Real-time monitoring** - Collects logs every 5 minutes (configurable)  
✅ **Security insights** - Track authentication failures and unusual patterns  
✅ **Performance metrics** - Authentication duration in microseconds  
✅ **Flexible configuration** - Customize time windows and collection intervals  
✅ **Dimension-rich metrics** - Filter by client IP, database, user, mechanism

## Architecture
```
MongoDB Atlas Logs (API)
    ↓
ActiveGate (Extension)
    ↓
Dynatrace Platform
    ↓
Metrics & Dashboards
```

The extension:
1. Calls MongoDB Atlas Administration API
2. Downloads and decompresses `.gz` log files
3. Parses JSON-formatted logs
4. Extracts connection/auth events
5. Aggregates by minute
6. Reports metrics to Dynatrace
