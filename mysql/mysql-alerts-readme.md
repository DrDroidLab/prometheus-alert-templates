# MySQL Prometheus Alert Templates

This document provides detailed information about MySQL Prometheus alert templates and how to set them up in your environment.

## Prerequisites

- Prometheus server (v2.x or higher)
- MySQL exporter (recommended: mysqld_exporter)
- MySQL instance (v5.7 or higher)
- Node exporter (for host metrics)

## Setup Instructions

### 1. Install MySQL Exporter

```bash
# Using Docker
docker run -d \
    --name mysqld_exporter \
    -p 9104:9104 \
    -e DATA_SOURCE_NAME="user:password@(hostname:3306)/" \
    prom/mysqld-exporter
```

### 2. Configure MySQL User for Monitoring

```sql
CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'password' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
```

### 3. Configure Prometheus

Add the following job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:9104']
    metrics_path: /metrics
```

### 4. Import Alert Rules

Copy the alert rules from `mysql-prometheus-alerts-template.yaml` to your Prometheus rules directory and reload Prometheus.

## Alert Rules Explanation

### Critical Alerts

1. **MySQLInstanceDown**
   - Triggers when MySQL instance is down for more than 1 minute
   - Critical severity
   - Immediate action required

2. **MySQLDiskSpaceCritical**
   - Triggers when disk space usage exceeds 85%
   - Critical severity
   - Action required to prevent database outage

### Warning Alerts

1. **MySQLHighThreadsRunning**
   - Monitors thread usage (>80% of max_connections)
   - Indicates potential connection pool exhaustion
   - Consider increasing max_connections or implementing connection pooling

2. **MySQLSlaveReplicationLag**
   - Alerts when replication lag exceeds 5 minutes
   - Important for maintaining high availability
   - Check network connectivity and replica performance

3. **MySQLInnoDBLogWaits**
   - Monitors InnoDB log write delays
   - Indicates potential I/O issues
   - Review storage performance

4. **MySQLSlowQueries**
   - Identifies slow-running queries
   - Helps in query optimization
   - Review and optimize slow queries

5. **MySQLHighConnectionLatency**
   - Monitors connection issues
   - May indicate network or resource problems
   - Review network and system resources

6. **MySQLTableLockContention**
   - Alerts on high table lock contention
   - May indicate application design issues
   - Review transaction patterns and table design

7. **MySQLHighCPUUsage**
   - Triggers when CPU usage exceeds 80%
   - May indicate need for query optimization
   - Review resource allocation

8. **MySQLBufferPoolUtilization**
   - Monitors InnoDB buffer pool usage
   - Critical for performance optimization
   - Consider adjusting buffer pool size

## Recommended Thresholds

The alert thresholds in these templates are based on general best practices but may need adjustment for your specific environment:

- Thread usage threshold: 80% of max_connections
- Replication lag: 5 minutes
- Disk space warning: 85%
- CPU usage warning: 80%
- Table lock contention: 10%
- InnoDB log waits: 10 per 15 minutes

## Tuning Recommendations

1. **Connection Management**
   - Adjust `max_connections` based on your application needs
   - Consider using connection pooling
   - Monitor `wait_timeout` and `interactive_timeout`

2. **InnoDB Settings**
   - Optimize `innodb_buffer_pool_size`
   - Monitor `innodb_log_file_size`
   - Adjust `innodb_flush_log_at_trx_commit` for performance/durability balance

3. **Query Performance**
   - Enable and monitor slow query log
   - Regular index maintenance
   - Query optimization and caching

## Grafana Integration

These metrics can be visualized in Grafana. Recommended panels:

1. Connection/Thread usage
2. Replication status
3. Query performance metrics
4. InnoDB metrics
5. Resource usage (CPU, Memory, Disk)

## Troubleshooting

### Common Issues

1. **Exporter Connection Issues**
   - Verify MySQL user permissions
   - Check network connectivity
   - Verify MySQL connection string

2. **Missing Metrics**
   - Check MySQL user privileges
   - Verify exporter is running
   - Check Prometheus scrape configuration

3. **False Positives**
   - Adjust alert thresholds
   - Add appropriate timing conditions
   - Consider adding more specific alert conditions

## Performance Optimization Tips

1. **Query Optimization**
   - Use EXPLAIN for query analysis
   - Maintain proper indexes
   - Regular query review and optimization

2. **System Configuration**
   - Optimize file system for MySQL
   - Configure appropriate swap settings
   - Monitor and adjust system limits

3. **Backup Impact**
   - Monitor backup impact on performance
   - Schedule backups during low-traffic periods
   - Consider using replica for backups

## Additional Resources

- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [mysqld_exporter Documentation](https://github.com/prometheus/mysqld_exporter)

## Support

For issues with these alert templates:
1. Verify MySQL exporter is working correctly
2. Check Prometheus logs
3. Review alert conditions and thresholds
4. Adjust based on your environment's specific needs 