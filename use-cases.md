# Use Cases

## 🔐 Security Monitoring

**Track failed authentication attempts** to detect potential security threats:
- Monitor authentication failures by IP address
- Identify brute-force attack patterns
- Alert on unusual authentication mechanisms
- Track authentication attempts from unexpected locations

**Example alert:** "More than 10 failed authentications from the same IP in 5 minutes"

## 📊 Connection Analysis

**Understand application connection patterns:**
- Monitor connection lifecycle (accepted → ended)
- Track connection duration
- Identify connection leaks
- Analyze load-balanced vs direct connections

**Example dashboard:** "Connection count by client IP over time"

## ⚡ Performance Optimization

**Analyze authentication performance:**
- Track authentication duration trends
- Identify slow authentication mechanisms
- Correlate auth performance with user/database
- Detect authentication bottlenecks

**Example metric:** "Average SCRAM-SHA-256 authentication duration by database"

## 🔍 Compliance & Audit

**Meet compliance requirements:**
- Log all authentication events
- Track who accessed which databases
- Monitor authentication methods used
- Generate audit reports from metrics

**Example report:** "All database access by user in the last 30 days"

## 🎯 Capacity Planning

**Plan infrastructure based on real data:**
- Understand connection patterns by time of day
- Identify peak usage periods
- Forecast connection growth
- Right-size MongoDB Atlas clusters

**Example insight:** "Connection count doubles between 9-10 AM on weekdays"
