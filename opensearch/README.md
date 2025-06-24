# OpenSearch Prometheus Alert Templates

This directory contains comprehensive Prometheus alerting rules for OpenSearch monitoring. These alerts are designed to provide maximum value based on SRE best practices and real-world operational experience.

## Overview

OpenSearch is a distributed, RESTful search and analytics engine. These alert templates cover critical aspects of OpenSearch operations including:

- **Cluster Health**: Overall cluster status and node availability
- **Shard Management**: Shard allocation, initialization, and relocation
- **Performance**: Search and indexing latency and throughput
- **Resource Usage**: JVM memory, disk space, CPU, and network
- **Cache Performance**: Query cache, request cache, and field data cache
- **Circuit Breakers**: Memory protection mechanisms
- **Thread Pools**: Task execution and queue management

## Prerequisites

### OpenSearch Metrics Exposure

OpenSearch metrics are exposed through the **Aiven prometheus-exporter-plugin-for-opensearch**:

#### Installation
```bash
# Install the plugin
sudo bin/opensearch-plugin install https://github.com/aiven/prometheus-exporter-plugin-for-opensearch/releases/download/2.11.1.0/prometheus-exporter-2.11.1.0.zip

# Restart OpenSearch
sudo systemctl restart opensearch
```

#### Configuration
```yaml
# opensearch.yml
prometheus.cluster.settings: true
prometheus.indices: true
prometheus.nodes.filter: "_local"
```

Access metrics at: `http://opensearch-node:9200/_prometheus/metrics`

### Metric Names Used

The alerts use actual OpenSearch Prometheus plugin metric names:

```
# Cluster Health
opensearch_cluster_status                    # 0=green, 1=yellow, 2=red
opensearch_cluster_shards_active_percent     # Percentage of active shards

# JVM Metrics
opensearch_jvm_mem_heap_used_percent        # JVM heap usage percentage

# System Metrics
opensearch_os_cpu_percent                   # CPU usage percentage

# Filesystem
opensearch_fs_path_available_bytes          # Available disk space
opensearch_fs_path_total_bytes              # Total disk space

# Indices Performance
opensearch_indices_search_query_time_seconds    # Search query time
opensearch_indices_search_query_count          # Search query count
opensearch_indices_indexing_index_time_seconds # Indexing time
opensearch_indices_indexing_index_count       # Indexing count

# Cache Metrics
opensearch_indices_fielddata_evictions_count   # Fielddata cache evictions

# Circuit Breakers
opensearch_breakers_tripped
opensearch_breakers_estimated_size_bytes
opensearch_breakers_limit_size_bytes

# Thread Pools
opensearch_thread_pool_rejected_count
opensearch_thread_pool_queue_count

# Transport
opensearch_transport_tx_size_bytes
opensearch_transport_rx_size_bytes

# Process
opensearch_process_cpu_percent
opensearch_os_load_average_1m
opensearch_os_cpu_count
```

## Alert Severity Levels

### Critical (Immediate Action Required)
- **OpenSearchDown**: Service is completely unavailable
- **OpenSearchClusterRed**: Cluster status is RED (status == 2)
- **OpenSearchNodeLeft**: Node has left the cluster
- **OpenSearchDataNodeLeft**: Data node has left the cluster
- **OpenSearchCriticalJVMMemoryUsage**: >95% JVM memory usage
- **OpenSearchCriticalDiskSpace**: <10% disk space remaining
- **OpenSearchUnassignedShards**: Active shards percentage < 100%

### Warning (Attention Needed)
- **OpenSearchClusterYellow**: Cluster status is YELLOW (status == 1)
- **OpenSearchHighHeapUsage**: >85% JVM heap usage
- **OpenSearchHighCPUUsage**: >80% CPU usage
- **OpenSearchHighDiskUsage**: >80% disk usage
- **OpenSearchHighFieldDataEvictions**: Field data eviction rate > 0/s
- **OpenSearchHighQueryLatency**: Average query latency > 0.5s
- **OpenSearchHighIndexingLatency**: Average indexing latency > 0.5s
- **OpenSearchLowDiskSpace**: <20% disk space remaining
- **OpenSearchHighSearchLatency**: Slow search performance
- **OpenSearchHighIndexingLatency**: Slow indexing performance
- **OpenSearchLowQueryCacheHitRate**: Poor cache performance
- **OpenSearchLowRequestCacheHitRate**: Poor request cache performance
- **OpenSearchHighCacheMemoryUsage**: Excessive cache memory usage
- **OpenSearchCircuitBreakerTripped**: Circuit breaker activated
- **OpenSearchCircuitBreakerNearLimit**: Circuit breaker near limit
- **OpenSearchThreadPoolRejections**: Thread pool rejecting tasks
- **OpenSearchHighThreadPoolQueueSize**: Thread pool queue growing
- **OpenSearchHighSystemLoad**: High system load average
- **OpenSearchHighSegmentCount**: Too many segments
- **OpenSearchFrequentFieldDataEvictions**: Frequent cache evictions
- **OpenSearchPendingTasks**: Cluster tasks pending

### Info (Monitoring)
- **OpenSearchRelocatingShards**: Shards are relocating
- **OpenSearchHighQueryLoad**: High query rate
- **OpenSearchHighIndexingLoad**: High indexing rate
- **OpenSearchHighNetworkUsage**: High network traffic
- **OpenSearchLowDocumentGrowth**: Low document growth rate

## Setup Instructions

### 1. Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: opensearch-alerts
data:
  opensearch-alerts.yaml: |
    # Paste the contents of opensearch-prometheus-alerts-template.yaml here
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: opensearch-alerts
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
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./opensearch-prometheus-alerts-template.yaml:/etc/prometheus/rules/opensearch.yml
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
  - "rules/opensearch-prometheus-alerts-template.yaml"

scrape_configs:
  - job_name: 'opensearch'
    static_configs:
      - targets: ['opensearch-node:9200']
    scrape_interval: 15s
    metrics_path: /_prometheus/metrics
```

## Prometheus Scrape Configuration

### Basic Configuration
```yaml
scrape_configs:
  - job_name: 'opensearch'
    static_configs:
      - targets: 
          - 'opensearch-node1:9200'
          - 'opensearch-node2:9200'
          - 'opensearch-node3:9200'
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /_prometheus/metrics
```

### With Authentication
```yaml
scrape_configs:
  - job_name: 'opensearch'
    static_configs:
      - targets: ['opensearch-node:9200']
    basic_auth:
      username: 'prometheus'
      password: 'your-password'
    metrics_path: /_prometheus/metrics
    scheme: https
    tls_config:
      insecure_skip_verify: true
```

### With Service Discovery (Kubernetes)
```yaml
scrape_configs:
  - job_name: 'opensearch'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: opensearch
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: http
```

## Alert Customization

### Adjusting Thresholds

Common threshold adjustments based on your environment:

```yaml
# JVM memory thresholds
- alert: OpenSearchHighJVMMemoryUsage
  expr: (opensearch_jvm_memory_used_bytes / opensearch_jvm_memory_max_bytes) * 100 > 80  # Reduced from 85%

# Search latency thresholds
- alert: OpenSearchHighSearchLatency
  expr: opensearch_indices_search_query_time_seconds / opensearch_indices_search_query_total > 0.5  # Reduced from 1s

# Cache hit rate thresholds
- alert: OpenSearchLowQueryCacheHitRate
  expr: (opensearch_indices_query_cache_hit_count / (opensearch_indices_query_cache_hit_count + opensearch_indices_query_cache_miss_count)) * 100 < 90  # Increased from 80%
```

### Environment-Specific Labels

Add environment labels to alerts:

```yaml
- alert: OpenSearchDown
  expr: up{job=~".*opensearch.*"} == 0
  labels:
    severity: critical
    environment: "{{ $labels.environment }}"
    team: "search-platform"
```

## Troubleshooting

### Common Issues

1. **No Metrics Available**
   - Verify prometheus-exporter plugin is installed and enabled
   - Check OpenSearch logs for plugin errors
   - Ensure Prometheus can reach OpenSearch nodes on port 9200

2. **Authentication Issues**
   - Configure proper authentication in Prometheus scrape config
   - Ensure prometheus user has necessary permissions
   - Check OpenSearch security plugin configuration

3. **High False Positive Rate**
   - Adjust thresholds based on your workload patterns
   - Consider cluster size when setting node-based alerts
   - Use appropriate evaluation periods for transient conditions

### Metric Validation

Test metric availability:

```bash
# Check if metrics endpoint is accessible
curl http://opensearch-node:9200/_prometheus/metrics

# With authentication
curl -u username:password https://opensearch-node:9200/_prometheus/metrics

# Query specific metrics in Prometheus
opensearch_cluster_status
up{job="opensearch"}
```

## Integration with Alertmanager

### Sample Alertmanager Configuration

```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'opensearch-alerts'
  routes:
    - match:
        service: opensearch
      receiver: 'opensearch-team'

receivers:
  - name: 'opensearch-team'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#opensearch-alerts'
        title: 'OpenSearch Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Monitoring Best Practices

### 1. Cluster Health Monitoring
- Always monitor cluster status (RED/YELLOW/GREEN)
- Set up alerts for node departures
- Monitor shard allocation issues

### 2. Performance Monitoring
- Track search and indexing latency
- Monitor JVM memory and GC performance
- Watch for circuit breaker activations

### 3. Resource Monitoring
- Monitor disk space across all data nodes
- Track CPU and memory usage
- Monitor network traffic for replication

### 4. Cache Optimization
- Monitor cache hit rates
- Track cache memory usage
- Watch for frequent evictions

## Related Documentation

- [OpenSearch Monitoring](https://opensearch.org/docs/latest/monitoring-your-cluster/)
- [OpenSearch Performance Tuning](https://opensearch.org/docs/latest/tuning-your-cluster/)
- [Prometheus Exporter Plugin](https://github.com/aiven/prometheus-exporter-plugin-for-opensearch)
- [OpenSearch Cluster Settings](https://opensearch.org/docs/latest/api-reference/cluster-settings/)

## Contributing

When contributing to these alert templates:

1. Ensure all metric names are verified against the Aiven prometheus-exporter plugin
2. Test alerts in a non-production environment first
3. Document any new thresholds or logic
4. Follow the existing severity classification system
5. Include appropriate `for` clauses to prevent alert flapping 