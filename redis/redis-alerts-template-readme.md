# Redis Alert Rules for Prometheus

This repository provides production-ready Redis monitoring alert rules that can be integrated into any existing Prometheus and Grafana setup. Whether you're running a simple Docker Compose stack or a full Kubernetes cluster, these alerts will help you monitor Redis health and performance.

## 🚨 Alert Rules Included

### Instance Availability
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisDown** | `up{job="redis"} == 0` | Critical | 0m | Immediate notification when Redis becomes unreachable |

### Memory Management
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisMemoryHigh** | Memory usage > 85% | Warning | 2m | Early warning before Redis hits memory limits |
| **RedisMemoryCritical** | Memory usage > 95% | Critical | 1m | Immediate action needed to prevent OOM kills |

### Connection Monitoring
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisConnectionsHigh** | Connected clients > 100 | Warning | 5m | Detect potential connection leaks or traffic spikes |
| **RedisRejectedConnections** | Any connection rejections in 5m | Critical | 0m | Redis is refusing new connections - immediate issue |

### Performance Monitoring
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisSlowQueries** | >10 slow queries in 5m | Warning | 2m | Identify performance bottlenecks |
| **RedisHighLatency** | Average latency > 0.1s | Warning | 5m | Detect degraded response times |
| **RedisCPUHigh** | CPU usage > 80% | Warning | 5m | Monitor Redis process resource usage |
| **RedisNetworkIOHigh** | Network I/O > 50MB/s | Warning | 5m | High network traffic detection |

### Data Management
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisKeyEvictions** | Any key evictions in 5m | Warning | 1m | Memory pressure causing data loss |
| **RedisKeyExpired** | >1000 key expirations in 5m | Info | 5m | Monitor key lifecycle patterns |
| **RedisLowHitRate** | Hit rate < 80% | Warning | 10m | Cache effectiveness monitoring |

### Persistence & Backup
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisRDBSaveFailed** | Last RDB save > 1 hour ago | Warning | 0m | Backup/persistence issues |
| **RedisAOFRewriteFailed** | AOF rewrite > 5 minutes | Warning | 0m | AOF persistence problems |

### Replication (for Cluster/Sentinel setups)
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **RedisReplicationLag** | Master has no connected slaves | Critical | 2m | Replication failure detection |
| **RedisReplicationBroken** | Slave lag > 1MB | Warning | 5m | Data consistency issues |

## 📋 Prerequisites

Before integrating these alerts, ensure you have:

1. **Prometheus** collecting Redis metrics
2. **Redis Exporter** exposing Redis metrics (usually on port 9121)
3. **Alertmanager** configured (required for alerts)
4. **Grafana** for visualization (optional)

## 🔧 Integration Methods

### Scenario 1: Docker Compose Setup

If you have an existing Docker Compose setup with Prometheus, add the Redis alert rules:

**Step 1: Add alerts directory to your Prometheus volume**
```yaml
# docker-compose.yml
services:
  prometheus:
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts:/etc/prometheus/alerts
      - prometheus_data:/prometheus
```

**Step 2: Update your prometheus.yml to include alert rules**
```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**Step 3: Copy the alert rules**
```bash
# Copy redis-alerts.yml to your prometheus/alerts/ directory
cp redis-alerts.yml ./prometheus/alerts/

# Restart Prometheus to load new rules
docker-compose restart prometheus
```

### Scenario 2: Kubernetes with kube-prometheus-stack

If you're using the popular `kube-prometheus-stack` Helm chart, choose one of these methods:

#### Option A: Values.yaml Method (Recommended)
Update your existing Helm values:

```yaml
# values.yaml
additionalPrometheusRulesMap:
  redis-alerts:
    groups:
    - name: redis_alerts
      rules:
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 0m
        labels:
          severity: critical
          service: redis
        annotations:
          summary: "Redis instance is down"
          description: "Redis instance {{ $labels.instance }} has been down for more than 0 minutes"
      # ... add all other rules from redis-alerts.yml
```

**Apply the update:**
```bash
helm upgrade prometheus-stack prometheus-community/kube-prometheus-stack \
  -f values.yaml \
  -n monitoring
```

#### Option B: PrometheusRule CRD
Create a separate PrometheusRule resource:

```yaml
# redis-prometheus-rule.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: redis-alerts
  namespace: monitoring
  labels:
    app.kubernetes.io/name: kube-prometheus-stack
    app.kubernetes.io/part-of: kube-prometheus-stack
spec:
  groups:
  - name: redis_alerts
    rules:
    - alert: RedisDown
      expr: up{job="redis"} == 0
      for: 0m
      labels:
        severity: critical
        service: redis
      annotations:
        summary: "Redis instance is down"
        description: "Redis instance {{ $labels.instance }} has been down for more than 0 minutes"
    # ... continue with all other alerts
```

**Apply the rule:**
```bash
kubectl apply -f redis-prometheus-rule.yaml
```

### Scenario 3: Kubernetes with Vanilla Prometheus Helm

If you're using the vanilla Prometheus Helm chart (not the kube-prometheus-stack):

#### Option A: Values.yaml Integration
Directly embed rules in your Helm values:

```yaml
# values.yaml
serverFiles:
  redis_alerts.yml:
    groups:
    - name: redis_alerts
      rules:
      # Copy all rules from redis-alerts.yml
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 0m
        labels:
          severity: critical
          service: redis
        annotations:
          summary: "Redis instance is down"
          description: "Redis instance {{ $labels.instance }} has been down for more than 0 minutes"
      # ... continue with all alerts
```

**Apply the update:**
```bash
helm upgrade prometheus prometheus-community/prometheus \
  -f values.yaml \
  -n monitoring
```

## 🛠 Ensuring Redis Metrics Collection

Make sure your setup is collecting Redis metrics:

### For Docker Compose
Ensure you have Redis Exporter in your docker-compose.yml:
```yaml
services:
  redis-exporter:
    image: oliver006/redis_exporter:latest
    environment:
      - REDIS_ADDR=redis://your-redis-host:6379
    ports:
      - "9121:9121"
```

### For Kubernetes
If using Bitnami Redis Helm chart with metrics:
```bash
helm upgrade redis bitnami/redis \
  --set metrics.enabled=true \
  --set metrics.serviceMonitor.enabled=true \
  -n your-namespace
```

Or deploy Redis Exporter separately:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-exporter
spec:
  template:
    spec:
      containers:
      - name: redis-exporter
        image: oliver006/redis_exporter:latest
        env:
        - name: REDIS_ADDR
          value: "redis://redis-service:6379"
```

## 🎛 Customizing Alert Thresholds

Modify the alert rules based on your requirements:

```yaml
# Adjust memory thresholds
- alert: RedisMemoryHigh
  expr: (redis_memory_used_bytes / redis_memory_max_bytes) * 100 > 90  # Changed from 85%
  for: 5m  # Wait 5 minutes before alerting

# Adjust connection limits
- alert: RedisConnectionsHigh
  expr: redis_connected_clients > 500  # Changed from 100
  for: 2m

# Add environment-specific labels
labels:
  severity: warning
  service: redis
  environment: production
  team: platform
```

## 🏥 Health Check

Verify alerts are loaded:

```bash
# Check Prometheus alerts
curl http://your-prometheus:9090/api/v1/rules

# Check specific Redis rules
curl "http://your-prometheus:9090/api/v1/rules?type=alert" | jq '.data.groups[] | select(.name=="redis_alerts")'
```

## 🐛 Troubleshooting

### Alerts Not Loading
1. **Check if rules are loaded in Prometheus:**
   ```bash
   kubectl port-forward svc/prometheus-server 9090:80 -n monitoring
   # Visit http://localhost:9090/rules to see loaded rules
   ```

2. **Verify Prometheus is scraping Redis:**
   ```bash
   curl "http://prometheus:9090/api/v1/query?query=up{job=\"redis\"}"
   ```

3. **Check alert rule syntax:**
   ```bash
   promtool check rules redis-alerts.yml
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| Rules not visible in Prometheus | Check ConfigMap/values.yaml is properly applied |
| No Redis metrics | Verify Redis Exporter is running and accessible |
| Alerts not firing | Check if metrics match the alert expressions |
| Wrong namespace | Ensure PrometheusRule is in the same namespace as Prometheus |

## 🌟 Production Best Practices

1. **Use proper labels for routing:**
   ```yaml
   labels:
     severity: critical
     service: redis
     team: platform
     environment: production
   ```

2. **Set appropriate `for` durations:**
   - Critical alerts: `0m` to `1m`
   - Warning alerts: `2m` to `5m`
   - Info alerts: `5m` to `10m`

3. **Add runbook links:**
   ```yaml
   annotations:
     runbook_url: "https://your-company.com/runbooks/redis"
     dashboard_url: "https://grafana.company.com/d/redis"
   ```

## 📚 Additional Resources

- [Redis Exporter Documentation](https://github.com/oliver006/redis_exporter)
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [kube-prometheus-stack Helm Chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)

---

**Quick Start:** Copy the contents of `redis-alerts.yml` and integrate using one of the three methods above based on your setup! 
