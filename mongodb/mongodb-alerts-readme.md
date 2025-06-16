# MongoDB Prometheus Alert Templates

This document provides detailed information about MongoDB Prometheus alert templates and how to set them up in your environment.

## Prerequisites

- Prometheus server (v2.x or higher)
- MongoDB exporter (recommended: mongodb_exporter)
- MongoDB instance (v4.x or higher)
- Node exporter (for host metrics)

## Setup Instructions

### 1. Install MongoDB Exporter

```bash
# Using Docker
docker run -d \
    --name mongodb_exporter \
    -p 9216:9216 \
    -e MONGODB_URI="mongodb://username:password@hostname:27017" \
    percona/mongodb_exporter
```

### 2. Configure MongoDB User for Monitoring

```javascript
use admin
db.createUser({
  user: "prometheus",
  pwd: "password",
  roles: [
    { role: "clusterMonitor", db: "admin" },
    { role: "read", db: "local" }
  ]
})
```

### 3. Configure Prometheus

Add the following job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mongodb'
    static_configs:
      - targets: ['localhost:9216']
    metrics_path: /metrics
```

### 4. Import Alert Rules

Copy the alert rules from `mongodb-prometheus-alerts-template.yaml` to your Prometheus rules directory and reload Prometheus.

## Alert Rules Explanation

### Critical Alerts

1. **MongoDBInstanceDown**
   - Triggers when MongoDB instance is down for more than 1 minute
   - Critical severity
   - Immediate action required

2. **MongoDBDiskSpaceCritical**
   - Triggers when disk space usage exceeds 85%
   - Critical severity
   - Action required to prevent database outage

### Warning Alerts

1. **MongoDBReplicationLag**
   - Alerts when replication lag exceeds 60 seconds
   - Important for maintaining high availability
   - Check network connectivity and replica performance

2. **MongoDBHighConnections**
   - Monitors connection usage (>80% of available connections)
   - Indicates potential connection pool exhaustion
   - Consider increasing maxConnections

3. **MongoDBHighLatency**
   - Monitors operation latency
   - Indicates potential performance issues
   - Review query patterns and indexes

4. **MongoDBWTCacheEvictions**
   - Monitors WiredTiger cache evictions
   - Indicates memory pressure
   - Consider increasing cache size

5. **MongoDBPageFaults**
   - Monitors page faults
   - Indicates memory pressure or disk I/O issues
   - Review memory allocation and disk performance

6. **MongoDBHighCPUUsage**
   - Triggers when CPU usage exceeds 80%
   - May indicate need for query optimization
   - Review resource allocation

7. **MongoDBCursorTimeout**
   - Monitors cursor timeouts
   - Indicates potential application issues
   - Review query patterns and cursor management

8. **MongoDBAssertRegular**
   - Monitors regular assertions
   - Indicates potential code or configuration issues
   - Review logs and application behavior

## Recommended Thresholds

The alert thresholds in these templates are based on general best practices but may need adjustment for your specific environment:

- Replication lag: 60 seconds
- Connection usage: 80% of available connections
- Operation latency: 100ms average
- Disk space warning: 85%
- CPU usage warning: 80%
- Cache evictions: 10 per 5 minutes
- Page faults: 10 per 5 minutes

## Tuning Recommendations

1. **Memory Management**
   - Optimize WiredTiger cache size
   - Monitor and adjust system memory limits
   - Consider using memory-mapped storage engine settings

2. **Connection Management**
   - Adjust maxConnections based on workload
   - Implement connection pooling
   - Monitor connection patterns

3. **Storage Configuration**
   - Use appropriate storage engine settings
   - Monitor disk I/O patterns
   - Regular storage maintenance

## Grafana Integration

These metrics can be visualized in Grafana. Recommended panels:

1. Connection usage
2. Replication status
3. Operation latency
4. WiredTiger metrics
5. Resource usage (CPU, Memory, Disk)

## Troubleshooting

### Common Issues

1. **Exporter Connection Issues**
   - Verify MongoDB user permissions
   - Check network connectivity
   - Verify MongoDB connection string

2. **Missing Metrics**
   - Check MongoDB user roles
   - Verify exporter is running
   - Check Prometheus scrape configuration

3. **False Positives**
   - Adjust alert thresholds
   - Add appropriate timing conditions
   - Consider adding more specific alert conditions

## Performance Optimization Tips

1. **Index Optimization**
   - Regular index usage analysis
   - Remove unused indexes
   - Create compound indexes when appropriate

2. **Query Optimization**
   - Use explain() for query analysis
   - Monitor slow queries
   - Implement proper query patterns

3. **Replication Configuration**
   - Monitor oplog size
   - Configure appropriate write concern
   - Regular replication health checks

## Backup Considerations

1. **Backup Strategy**
   - Regular backup scheduling
   - Monitor backup impact on performance
   - Test restore procedures

2. **Backup Verification**
   - Validate backup integrity
   - Monitor backup size and duration
   - Regular restore testing

## Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [MongoDB Exporter Documentation](https://github.com/percona/mongodb_exporter)

## Support

For issues with these alert templates:
1. Verify MongoDB exporter is working correctly
2. Check Prometheus logs
3. Review alert conditions and thresholds
4. Adjust based on your environment's specific needs 