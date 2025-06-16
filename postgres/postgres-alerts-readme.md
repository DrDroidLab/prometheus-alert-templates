# PostgreSQL Prometheus Alert Templates

This document provides detailed information about PostgreSQL-specific Prometheus alert templates. For general Prometheus setup instructions, please refer to the [main README](../README.md).

## Prerequisites

- PostgreSQL instance (v10 or higher)
- PostgreSQL exporter (recommended: postgres_exporter)

## Exporter Setup

### Configure PostgreSQL User for Monitoring

```sql
CREATE USER postgres_exporter WITH PASSWORD 'password';
GRANT pg_monitor TO postgres_exporter;
```

### Configure PostgreSQL Exporter

```bash
# Using Docker
docker run -d \
    --name postgres_exporter \
    -p 9187:9187 \
    -e DATA_SOURCE_NAME="postgresql://postgres_exporter:password@hostname:5432/database?sslmode=disable" \
    quay.io/prometheuscommunity/postgres-exporter
```

## Alert Rules Explanation

### Critical Alerts

1. **PostgresInstanceDown**
   - Triggers when PostgreSQL instance is down for more than 1 minute
   - Critical severity
   - Immediate action required

2. **PostgresDiskSpaceCritical**
   - Triggers when disk space usage exceeds 85%
   - Critical severity
   - Action required to prevent database outage

### Warning Alerts

1. **PostgresHighConnections**
   - Monitors connection pool usage (>80% of max_connections)
   - Indicates potential connection pool exhaustion
   - Consider increasing max_connections or implementing connection pooling

2. **PostgresReplicationLag**
   - Alerts when replication lag exceeds 100MB
   - Important for maintaining high availability
   - Check network connectivity and replica performance

3. **PostgresSlowQueries**
   - Identifies queries taking longer than 5 minutes
   - Helps in query optimization
   - Review and optimize slow queries

4. **PostgresDeadlocks**
   - Monitors for database deadlocks
   - Indicates potential application issues
   - Review application logic and transaction management

5. **PostgresHighRollbacks**
   - Alerts when rollback rate exceeds 2%
   - High rollbacks may indicate application issues
   - Investigate transaction patterns

6. **PostgresHighCPUUsage**
   - Triggers when CPU usage exceeds 80%
   - May indicate need for query optimization or scaling
   - Review resource allocation

7. **PostgresCheckpointsTooFrequent**
   - Monitors checkpoint frequency
   - Frequent checkpoints can impact performance
   - Adjust checkpoint-related parameters

## Recommended Thresholds

The alert thresholds in these templates are based on general best practices but may need adjustment for your specific environment:

- Connection threshold: 80% of max_connections
- Replication lag: 100MB
- Slow query threshold: 5 minutes
- Disk space warning: 85%
- CPU usage warning: 80%
- Rollback rate: 2%

## PostgreSQL-Specific Tuning

1. **Connection Pool**
   - Adjust `max_connections` based on your application needs
   - Consider using connection pooling (pgBouncer)
   - Monitor connection states and durations

2. **Replication**
   - Monitor `wal_keep_segments` and `max_wal_senders`
   - Adjust network capacity for replication traffic
   - Configure appropriate replication slots

3. **Query Performance**
   - Regular VACUUM and ANALYZE
   - Index maintenance
   - Query optimization
   - Monitor and adjust work_mem

4. **Checkpoint Configuration**
   - Adjust `checkpoint_timeout`
   - Configure `checkpoint_completion_target`
   - Monitor checkpoint timing and I/O impact

## Grafana Dashboard Recommendations

Key metrics to monitor in Grafana:

1. Connection Metrics
   - Active connections
   - Connection states
   - Connection duration

2. Query Performance
   - Query execution time
   - Slow query count
   - Query cache hit ratio

3. Replication Status
   - Replication lag
   - WAL generation rate
   - Replication slot status

4. Resource Usage
   - CPU utilization
   - Memory usage
   - Disk I/O
   - Cache hit ratios

## Troubleshooting Common Alerts

1. **High Connections**
   - Check for connection leaks
   - Review connection pooling settings
   - Monitor application connection patterns

2. **Replication Lag**
   - Check network bandwidth
   - Monitor WAL generation rate
   - Review replica server resources

3. **Slow Queries**
   - Use EXPLAIN ANALYZE
   - Review index usage
   - Check for table bloat

4. **Deadlocks**
   - Review transaction patterns
   - Check for lock contention
   - Monitor lock wait times

## Additional PostgreSQL Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Monitoring Guide](https://www.postgresql.org/docs/current/monitoring.html)
- [postgres_exporter Documentation](https://github.com/prometheus-community/postgres_exporter) 