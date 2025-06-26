# Cassandra Prometheus Alert Templates

This directory contains comprehensive Prometheus alerting rules for Cassandra monitoring. These alerts are designed to provide maximum value based on SRE best practices and real-world operational experience.

## Overview

Apache Cassandra is a distributed NoSQL database designed for handling large amounts of data across many commodity servers. These alert templates cover critical aspects of Cassandra operations including:

- **Node Health**: Service availability and connectivity
- **Performance**: Read/write latency and throughput
- **Compaction**: Background maintenance operations
- **Storage**: SSTable management and disk usage
- **Dropped Messages**: Network and coordination issues
- **Thread Pools**: Task execution and queue management
- **Memory and Cache**: JVM memory and cache performance
- **Hints and Repair**: Data consistency mechanisms

## Prerequisites

### Cassandra Metrics Exposure

Cassandra metrics are exposed through JMX-based Prometheus exporters:

#### Option 1: Criteo Cassandra Exporter (Recommended)
```bash
# Download and run the exporter
wget https://github.com/criteo/cassandra_exporter/releases/download/2.3.8/cassandra_exporter-2.3.8-all.jar

# Run the exporter
java -jar cassandra_exporter-2.3.8-all.jar config.yml
```

#### Option 2: Instaclustr Cassandra Exporter
```bash
# Download and run the exporter
wget https://github.com/instaclustr/cassandra-exporter/releases/download/v0.9.10/cassandra-exporter-0.9.10.jar

# Run the exporter
java -jar cassandra-exporter-0.9.10.jar
```

#### Docker Installation
```bash
docker run -d \
  --name cassandra_exporter \
  -p 8080:8080 \
  -e CASSANDRA_EXPORTER_CONFIG_host=cassandra-host \
  -e CASSANDRA_EXPORTER_CONFIG_port=7199 \
  criteord/cassandra_exporter:latest
```

Access metrics at: `http://exporter-host:8080/metrics`

### Metric Names Used

The alerts use actual Cassandra JMX metric names exposed by the exporters:

```
# Connection Metrics
cassandra_client_connected_native_clients
cassandra_client_connected_thrift_clients

# Latency Metrics
cassandra_table_read_latency_95th_percentile
cassandra_table_write_latency_95th_percentile

# Compaction Metrics
cassandra_compaction_pending_tasks
cassandra_compaction_aborted

# SSTable Metrics
cassandra_table_live_ss_table_count
cassandra_table_ss_tables_per_read_histogram_95th_percentile

# Dropped Messages
cassandra_dropped_message_dropped{name="MUTATION"}
cassandra_dropped_message_dropped{name="READ"}
cassandra_dropped_message_dropped{name="RANGE_SLICE"}

# Thread Pool Metrics
cassandra_thread_pools_currently_blocked_tasks
cassandra_thread_pools_pending_tasks

# Cache Metrics
cassandra_cache_hit_rate{cache="KeyCache"}

# Storage Metrics
cassandra_storage_total_hints
cassandra_hints_service_hints_failed

# Client Request Metrics
cassandra_client_request_timeouts
cassandra_client_request_unavailables

# Table Metrics
cassandra_table_total_disk_space_used
cassandra_table_max_partition_size
cassandra_table_tombstones_scanned_histogram_95th_percentile
cassandra_table_bloom_filter_false_ratio
cassandra_table_speculative_retries

# CQL Metrics
cassandra_cql_regular_statements_executed

# Commit Log Metrics
cassandra_commit_log_waiting_on_commit_count
cassandra_commit_log_waiting_on_commit_95th_percentile
```

## Alert Severity Levels

### Critical (Immediate Action Required)
- **CassandraDown**: Service is completely unavailable
- **CassandraCriticalReadLatency**: >1000ms read latency
- **CassandraCriticalWriteLatency**: >500ms write latency
- **CassandraCriticalPendingCompactions**: >100 pending compactions
- **CassandraDroppedMutations**: Write operations being dropped
- **CassandraHighUnavailables**: Unavailable exceptions occurring
- **CassandraMemtableFlushWriterBlocked**: Critical memory pressure

### Warning (Attention Needed)
- **CassandraHighNativeConnections**: High client connection count
- **CassandraHighThriftConnections**: High thrift connection count
- **CassandraHighReadLatency**: >100ms read latency
- **CassandraHighWriteLatency**: >50ms write latency
- **CassandraHighPendingCompactions**: >30 pending compactions
- **CassandraCompactionAborted**: Compactions being aborted
- **CassandraHighSSTableCount**: >200 SSTables per table
- **CassandraHighSSTablesPerRead**: >10 SSTables per read
- **CassandraDroppedReads**: Read operations being dropped
- **CassandraDroppedRangeSlice**: Range queries being dropped
- **CassandraThreadPoolBlocked**: Thread pool tasks blocked
- **CassandraHighThreadPoolPending**: >100 pending tasks
- **CassandraLowKeyCacheHitRate**: <90% key cache hit rate
- **CassandraHintsOnDisk**: Hints accumulating on disk
- **CassandraHintReplayFailed**: Hint replay failures
- **CassandraHighTimeouts**: Request timeouts occurring
- **CassandraHighDiskUsage**: >100GB table disk usage
- **CassandraLargePartitions**: >100MB partitions detected
- **CassandraHighTombstones**: >1000 tombstones per read
- **CassandraHighBloomFilterFalsePositives**: >10% false positive rate
- **CassandraHighSpeculativeRetries**: >10 speculative retries/sec
- **CassandraCommitLogWaiting**: Operations waiting on commit log
- **CassandraHighCommitLogWaitTime**: >100ms commit log wait time

### Info (Monitoring)
- **CassandraHighCQLStatements**: >1000 CQL statements/sec

## Setup Instructions

### 1. Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cassandra-alerts
data:
  cassandra-alerts.yaml: |
    # Paste the contents of cassandra-prometheus-alerts-template.yaml here
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cassandra-alerts
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
    # Include the alert groups from the template
```

### 2. Docker Compose Setup

```yaml
version: '3.8'
services:
  cassandra_exporter:
    image: criteord/cassandra_exporter:latest
    environment:
      - CASSANDRA_EXPORTER_CONFIG_host=cassandra
      - CASSANDRA_EXPORTER_CONFIG_port=7199
    ports:
      - "8080:8080"
    depends_on:
      - cassandra

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./cassandra-prometheus-alerts-template.yaml:/etc/prometheus/rules/cassandra.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
```

### 3. Standalone Prometheus

Add to your `prometheus.yml`:

```yaml
rule_files:
  - "rules/cassandra-prometheus-alerts-template.yaml"

scrape_configs:
  - job_name: 'cassandra'
    static_configs:
      - targets: ['cassandra-exporter:8080']
    scrape_interval: 15s
```

## Prometheus Scrape Configuration

### Basic Configuration
```yaml
scrape_configs:
  - job_name: 'cassandra'
    static_configs:
      - targets: 
          - 'cassandra-exporter1:8080'
          - 'cassandra-exporter2:8080'
          - 'cassandra-exporter3:8080'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### With Service Discovery (Kubernetes)
```yaml
scrape_configs:
  - job_name: 'cassandra'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: cassandra-exporter
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: metrics
```

## Alert Customization

### Adjusting Thresholds

Common threshold adjustments based on your environment:

```yaml
# Latency thresholds for faster SLA requirements
- alert: CassandraHighReadLatency
  expr: cassandra_table_read_latency_95th_percentile > 50  # Reduced from 100ms

# Connection thresholds for smaller deployments
- alert: CassandraHighNativeConnections
  expr: cassandra_client_connected_native_clients > 200  # Reduced from 500

# Compaction thresholds for write-heavy workloads
- alert: CassandraHighPendingCompactions
  expr: cassandra_compaction_pending_tasks > 50  # Increased from 30
```

### Environment-Specific Labels

Add environment labels to alerts:

```yaml
- alert: CassandraDown
  expr: up{job=~".*cassandra.*"} == 0
  labels:
    severity: critical
    environment: "{{ $labels.environment }}"
    team: "data-platform"
```

## Troubleshooting

### Common Issues

1. **No Metrics Available**
   - Verify JMX is enabled on Cassandra nodes (port 7199)
   - Check cassandra_exporter connectivity to Cassandra JMX
   - Ensure Prometheus can reach the exporter

2. **JMX Authentication Issues**
   - Configure JMX authentication in cassandra-env.sh
   - Update exporter configuration with JMX credentials
   - Verify JMX user permissions

3. **High False Positive Rate**
   - Adjust thresholds based on your workload patterns
   - Consider cluster size and replication factor
   - Use appropriate evaluation periods for transient conditions

### Metric Validation

Test metric availability:

```bash
# Check if exporter metrics endpoint is accessible
curl http://cassandra-exporter:8080/metrics

# Test JMX connectivity
nodetool status  # From Cassandra node

# Query specific metrics in Prometheus
cassandra_table_read_latency_95th_percentile
up{job="cassandra"}
```

## Integration with Alertmanager

### Sample Alertmanager Configuration

```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'cassandra-alerts'
  routes:
    - match:
        service: cassandra
      receiver: 'cassandra-team'

receivers:
  - name: 'cassandra-team'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#cassandra-alerts'
        title: 'Cassandra Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Monitoring Best Practices

### 1. Latency Monitoring
- Monitor both read and write latency percentiles
- Set different thresholds for different consistency levels
- Track latency trends over time

### 2. Compaction Management
- Monitor pending compaction tasks
- Watch for compaction aborts
- Track SSTable count per table

### 3. Dropped Messages
- Zero tolerance for dropped mutations (writes)
- Monitor read drops during high load
- Track timeout patterns

### 4. Resource Monitoring
- Monitor JVM heap usage
- Track disk space per node
- Watch for large partitions

### 5. Consistency Monitoring
- Monitor hint accumulation
- Track repair operations
- Watch for unavailable exceptions

## Related Documentation

- [Cassandra Monitoring](https://cassandra.apache.org/doc/latest/operating/metrics.html)
- [Cassandra Performance Tuning](https://cassandra.apache.org/doc/latest/operating/hardware.html)
- [Criteo Cassandra Exporter](https://github.com/criteo/cassandra_exporter)
- [Instaclustr Cassandra Exporter](https://github.com/instaclustr/cassandra-exporter)
- [Cassandra JMX Metrics](https://cassandra.apache.org/doc/latest/operating/metrics.html)

## Contributing

When contributing to these alert templates:

1. Ensure all metric names are verified against actual Cassandra JMX exporters
2. Test alerts in a non-production environment first
3. Document any new thresholds or logic
4. Follow the existing severity classification system
5. Include appropriate `for` clauses to prevent alert flapping
6. Consider different Cassandra versions and their metric variations 