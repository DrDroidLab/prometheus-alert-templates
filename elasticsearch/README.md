# Elasticsearch Prometheus Alert Templates

This directory contains comprehensive Prometheus alerting rules for Elasticsearch monitoring. These alerts are designed to provide maximum value based on SRE best practices and real-world operational experience.

## Overview

Elasticsearch is a distributed, RESTful search and analytics engine. These alert templates cover critical aspects of Elasticsearch operations including:

- **Cluster Health**: Overall cluster status and node availability
- **Shard Management**: Shard allocation and distribution
- **Performance**: Search and indexing latency
- **Resource Usage**: JVM memory, disk space, and CPU
- **Cache Performance**: Field data cache usage

## Prerequisites

### Elasticsearch Metrics Exposure

Elasticsearch metrics are exposed through the Prometheus exporter. The exporter is available at port 9114 by default.

### Metric Names Used

The alerts use the following Elasticsearch Prometheus metric names:

```
# Basic Metrics
up{job=~".*elasticsearch.*"}                # Elasticsearch instance availability

# Cluster Health
elasticsearch_cluster_health_status         # Status with color label (red, yellow, green)
elasticsearch_cluster_health_unassigned_shards  # Number of unassigned shards

# JVM Metrics
elasticsearch_jvm_memory_used_bytes         # Used memory with area="heap"
elasticsearch_jvm_memory_max_bytes          # Max memory with area="heap"

# System Metrics
elasticsearch_process_cpu_percent           # CPU usage percentage

# Filesystem
elasticsearch_filesystem_data_available_bytes  # Available disk space
elasticsearch_filesystem_data_size_bytes      # Total disk space

# Indices Performance
elasticsearch_indices_search_query_time_seconds      # Search query time
elasticsearch_indices_indexing_index_time_seconds_total  # Indexing time

# Cache Metrics
elasticsearch_indices_fielddata_memory_size_bytes    # Fielddata cache size
```

## Alert Severity Levels

### Critical (Immediate Action Required)
- **ElasticsearchDown**: Service is completely unavailable
- **ElasticsearchClusterRed**: Cluster status is RED
- **ElasticsearchUnassignedShards**: Cluster has unassigned shards

### Warning (Attention Needed)
- **ElasticsearchClusterYellow**: Cluster status is YELLOW
- **ElasticsearchHighHeapUsage**: >85% JVM heap usage
- **ElasticsearchHighCPUUsage**: >80% CPU usage
- **ElasticsearchHighDiskUsage**: <20% disk space remaining
- **ElasticsearchHighFieldDataCache**: Fielddata cache size >1GB
- **ElasticsearchHighSearchLatency**: Search latency >0.5s
- **ElasticsearchHighIndexingLatency**: Indexing latency >0.5s

### Info (Monitoring)
- **ElasticsearchRelocatingShards**: Shards are relocating
- **ElasticsearchHighQueryLoad**: High query rate
- **ElasticsearchHighIndexingLoad**: High indexing rate
- **ElasticsearchHighNetworkUsage**: High network traffic
- **ElasticsearchLowDocumentGrowth**: Low document growth rate
- **ElasticsearchIndexSizeGrowth**: Large index growth

## Setup Instructions

### 1. Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: elasticsearch-alerts
data:
  elasticsearch-alerts.yaml: |
    # Paste the contents of elasticsearch-prometheus-alerts-template.yaml here
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: elasticsearch-alerts
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
  elasticsearch_exporter:
    image: quay.io/prometheuscommunity/elasticsearch-exporter:latest
    command:
      - '--es.uri=http://elasticsearch:9200'
    ports:
      - "9114:9114"
    depends_on:
      - elasticsearch

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./elasticsearch-prometheus-alerts-template.yaml:/etc/prometheus/rules/elasticsearch.yml
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
  - "rules/elasticsearch-prometheus-alerts-template.yaml"

scrape_configs:
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch-exporter:9114']
    scrape_interval: 15s
```

## Prometheus Scrape Configuration

### Basic Configuration
```yaml
scrape_configs:
  - job_name: 'elasticsearch'
    static_configs:
      - targets: 
          - 'elasticsearch-exporter1:9114'
          - 'elasticsearch-exporter2:9114'
          - 'elasticsearch-exporter3:9114'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### With Service Discovery (Kubernetes)
```yaml
scrape_configs:
  - job_name: 'elasticsearch'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: elasticsearch-exporter
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: metrics
```

## Alert Customization

### Adjusting Thresholds

Common threshold adjustments based on your environment:

```yaml
# JVM memory thresholds
- alert: ElasticsearchHighJVMMemoryUsage
  expr: (elasticsearch_jvm_memory_used_bytes / elasticsearch_jvm_memory_max_bytes) * 100 > 80  # Reduced from 85%

# Search latency thresholds
- alert: ElasticsearchHighSearchLatency
  expr: elasticsearch_indices_search_query_time_seconds / elasticsearch_indices_search_query_total > 0.5  # Reduced from 1s

# Cache hit rate thresholds
- alert: ElasticsearchLowQueryCacheHitRate
  expr: (elasticsearch_indices_query_cache_count{type="hit"} / (elasticsearch_indices_query_cache_count{type="hit"} + elasticsearch_indices_query_cache_count{type="miss"})) * 100 < 90  # Increased from 80%
```

### Environment-Specific Labels

Add environment labels to alerts:

```yaml
- alert: ElasticsearchDown
  expr: up{job=~".*elasticsearch.*"} == 0
  labels:
    severity: critical
    environment: "{{ $labels.environment }}"
    team: "search-platform"
```

## Troubleshooting

### Common Issues

1. **No Metrics Available**
   - Verify elasticsearch_exporter is running and accessible
   - Check Elasticsearch cluster connectivity from exporter
   - Ensure Prometheus can reach the exporter on port 9114

2. **Authentication Issues**
   - Configure elasticsearch_exporter with proper credentials
   - Use `--es.username` and `--es.password` flags
   - For X-Pack security, ensure proper user permissions

3. **High False Positive Rate**
   - Adjust thresholds based on your workload patterns
   - Consider cluster size when setting node-based alerts
   - Use appropriate evaluation periods for transient conditions

### Metric Validation

Test metric availability:

```bash
# Check if exporter metrics endpoint is accessible
curl http://elasticsearch-exporter:9114/metrics

# Query specific metrics in Prometheus
elasticsearch_cluster_health_status
up{job="elasticsearch"}
```

## Integration with Alertmanager

### Sample Alertmanager Configuration

```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'elasticsearch-alerts'
  routes:
    - match:
        service: elasticsearch
      receiver: 'elasticsearch-team'

receivers:
  - name: 'elasticsearch-team'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#elasticsearch-alerts'
        title: 'Elasticsearch Alert: {{ .GroupLabels.alertname }}'
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

### 4. Index Management
- Monitor ILM status and operations
- Track index size growth
- Watch for snapshot failures

## Related Documentation

- [Elasticsearch Monitoring](https://www.elastic.co/guide/en/elasticsearch/reference/current/monitoring.html)
- [Elasticsearch Performance Tuning](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-for-search-speed.html)
- [Prometheus Elasticsearch Exporter](https://github.com/prometheus-community/elasticsearch_exporter)
- [Elasticsearch Cluster Settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-update-settings.html)

## Contributing

When contributing to these alert templates:

1. Ensure all metric names are verified against the prometheus-community/elasticsearch_exporter
2. Test alerts in a non-production environment first
3. Document any new thresholds or logic
4. Follow the existing severity classification system
5. Include appropriate `for` clauses to prevent alert flapping 