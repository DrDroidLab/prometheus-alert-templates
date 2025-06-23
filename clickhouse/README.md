# ClickHouse Prometheus Alert Templates

This directory contains Prometheus alerting rules for ClickHouse monitoring. These alerts are designed to provide essential monitoring for ClickHouse instances based on actual metrics exposed by ClickHouse's built-in Prometheus exporter.

## Alert Overview

### Critical Alerts

1. **ClickHouseDown**
   - Triggers when ClickHouse instance is unreachable
   - Metric: `up{job=~".*clickhouse.*"}`
   - Threshold: Instance down for > 1 minute

2. **ClickHouseRejectedConnections**
   - Triggers when ClickHouse starts rejecting connections
   - Metrics: `ClickHouseAsyncMetrics_TCPRejectedConnections`, `ClickHouseAsyncMetrics_HTTPRejectedConnections`
   - Threshold: Any connection rejections in 5 minutes

3. **ClickHouseMemoryLimitExceeded**
   - Triggers when queries hit memory limits
   - Metric: `ClickHouseProfileEvents_QueryMemoryLimitExceeded`
   - Threshold: Any memory limit exceeded events in 5 minutes

### Warning Alerts

1. **ClickHouseHighMemoryUsage**
   - Monitors memory usage relative to system memory
   - Metrics: `ClickHouseAsyncMetrics_MemoryResident`, `ClickHouseAsyncMetrics_OSMemoryTotal`
   - Threshold: > 85% memory usage for 5 minutes

2. **ClickHouseSlowQueries**
   - Detects slow-running queries
   - Metric: `ClickHouseProfileEvents_QueryTimeMicroseconds`
   - Threshold: Queries taking > 1 second

3. **ClickHouseHighCPUUsage**
   - Monitors CPU utilization
   - Metric: `ClickHouseProfileEvents_UserTimeMicroseconds`
   - Threshold: > 80% CPU usage for 5 minutes

4. **ClickHouseDistributedSyncInsertErrors**
   - Monitors distributed insert issues with read-only replicas
   - Metric: `ClickHouseProfileEvents_DistributedConnectionSkipReadOnlyReplica`
   - Threshold: Any skipped replicas in 5 minutes

5. **ClickHouseReadOnlyReplicas**
   - Detects tables in read-only state
   - Metric: `ClickHouseMetrics_ReadonlyReplica`
   - Threshold: Any tables in read-only state for 5 minutes

6. **ClickHouseBackgroundTasksOverload**
   - Monitors background processing pools utilization
   - Metrics: 
     - `ClickHouseMetrics_BackgroundSchedulePoolTask`
     - `ClickHouseMetrics_BackgroundSchedulePoolSize`
     - `ClickHouseMetrics_BackgroundMergesAndMutationsPoolTask`
     - `ClickHouseMetrics_BackgroundMergesAndMutationsPoolSize`
   - Threshold: > 80% pool utilization for 5 minutes

7. **ClickHouseDelayedInserts**
   - Monitors insert operations being delayed
   - Metric: `ClickHouseMetrics_DelayedInserts`
   - Threshold: Any delayed inserts for 5 minutes

## Metric Categories

ClickHouse exposes metrics with different prefixes:

1. **ClickHouseMetrics_**: Current state metrics
2. **ClickHouseProfileEvents_**: Cumulative event counters
3. **ClickHouseAsyncMetrics_**: Periodically updated metrics
4. **ClickHouseErrorMetric_**: Error counters

## Setup Instructions

### 1. Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'clickhouse'
    static_configs:
      - targets: ['clickhouse:9363']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### 2. Docker Setup

The alerts are tested with the following ClickHouse configuration:

```yaml
version: '3.8'
services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"  # HTTP interface
      - "9000:9000"  # Native interface
      - "9363:9363"  # Prometheus metrics
    volumes:
      - ./clickhouse/config.xml:/etc/clickhouse-server/config.d/prometheus.xml:ro
```

Required Prometheus export configuration (`config.xml`):

```xml
<?xml version="1.0"?>
<clickhouse>
    <prometheus>
        <endpoint>/metrics</endpoint>
        <port>9363</port>
        <metrics>true</metrics>
        <events>true</events>
        <asynchronous_metrics>true</asynchronous_metrics>
        <status_info>true</status_info>
    </prometheus>
</clickhouse>
```

## Alert Customization

Adjust thresholds based on your environment:

```yaml
# Example: Lower memory threshold for smaller instances
- alert: ClickHouseHighMemoryUsage
  expr: ClickHouseAsyncMetrics_MemoryResident / ClickHouseAsyncMetrics_OSMemoryTotal * 100 > 75

# Example: More aggressive CPU monitoring
- alert: ClickHouseHighCPUUsage
  expr: rate(ClickHouseProfileEvents_UserTimeMicroseconds[5m]) > 0.7 * 1000000
```

## Troubleshooting

1. **No Metrics Available**
   - Verify ClickHouse is running: `curl http://localhost:8123/`
   - Check Prometheus endpoint: `curl http://localhost:9363/metrics`
   - Ensure proper configuration in `config.xml`

2. **False Positives**
   - Adjust `for` duration in alerts
   - Review and adjust thresholds
   - Consider adding additional conditions to alerts

## Related Documentation

- [ClickHouse Monitoring](https://clickhouse.com/docs/en/operations/monitoring)
- [ClickHouse System Tables](https://clickhouse.com/docs/en/operations/system-tables)
- [ClickHouse Prometheus Integration](https://clickhouse.com/docs/en/operations/monitoring/prometheus) 