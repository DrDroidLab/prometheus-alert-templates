# Kubernetes Alert Rules for Prometheus

This repository provides production-ready Kubernetes monitoring alert rules that can be integrated into any existing Prometheus and Grafana setup. These alerts cover critical aspects of Kubernetes cluster monitoring, from node health to application deployments.

## 🚨 Alert Rules Overview

### Node Monitoring
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sNodeNotReady** | Node not in Ready state | Critical | 5m | Detect node failures |
| **K8sNodeDiskPressure** | Node under disk pressure | Critical | 5m | Prevent node storage issues |

### Pod Health
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sPodCrashLooping** | Pod restarts > 2.5/hour | Critical | 1m | Detect application stability issues |
| **K8sPodHighMemoryUsage** | Memory usage > 85% | Warning | 5m | Prevent memory-related crashes |
| **K8sPodHighCpuUsage** | CPU usage > 85% | Warning | 5m | Detect performance bottlenecks |
| **K8sPodImagePullBackOff** | Image pull failures | Critical | 5m | Identify deployment issues |
| **K8sPodStuckInPending** | Pod stuck in Pending | Warning | 15m | Detect scheduling problems |
| **K8sPodOOMKilled** | Container OOM killed | Critical | 0m | Memory limit violations |

### Deployment Management
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sDeploymentReplicasMismatch** | Available ≠ Desired replicas | Warning | 15m | Deployment health check |
| **K8sDeploymentGenerationMismatch** | Deployment not progressing | Warning | 5m | Rollout issues detection |

### Service Availability
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sServiceEndpointDown** | No endpoints available | Critical | 5m | Service availability monitoring |

### Storage
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sPVCPending** | PVC in Pending state | Warning | 5m | Storage provisioning issues |

### Jobs and CronJobs
| Alert | Condition | Severity | Duration | Purpose |
|-------|-----------|----------|----------|---------|
| **K8sJobFailed** | Job failure detected | Warning | 0m | Batch job monitoring |
| **K8sCronJobSuspended** | CronJob suspended | Info | 0m | Scheduled job status |

## 📋 Prerequisites

Before implementing these alerts, ensure you have:

1. **Prometheus Operator** or vanilla **Prometheus** installed in your cluster
2. **kube-state-metrics** deployed for Kubernetes object metrics
3. **node-exporter** for node-level metrics
4. **Alertmanager** configured for alert routing
5. **Grafana** (optional) for visualization

## 🔧 Integration Methods

### Method 1: Using Prometheus Operator (Recommended)

If you're using the Prometheus Operator (e.g., kube-prometheus-stack), create a PrometheusRule custom resource:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: kubernetes-alerts
  namespace: monitoring
  labels:
    release: prometheus # Match your Prometheus Operator release label
spec:
  groups:
    - name: kubernetes-alerts
      rules:
        # Copy rules from kubernetes-alerts-template.yml
```

Apply using:
```bash
kubectl apply -f kubernetes-prometheus-rules.yaml
```

### Method 2: Direct Prometheus Configuration

For vanilla Prometheus installations:

1. Mount the alerts file into your Prometheus container:
```yaml
# prometheus-deployment.yaml
volumes:
  - name: prometheus-alerts
    configMap:
      name: kubernetes-alerts
```

2. Update prometheus.yml to include the rules:
```yaml
rule_files:
  - /etc/prometheus/alerts/kubernetes-alerts.yml
```

3. Create a ConfigMap with the alerts:
```bash
kubectl create configmap kubernetes-alerts --from-file=kubernetes-alerts.yml
```

## 📊 Metric Collection Setup

### Required Exporters

1. **kube-state-metrics**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install kube-state-metrics prometheus-community/kube-state-metrics
   ```

2. **node-exporter**
   ```bash
   helm install node-exporter prometheus-community/prometheus-node-exporter
   ```

### Prometheus Scrape Configurations

Ensure your Prometheus is configured to scrape these targets:

```yaml
scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

## ⚙️ Customization Guidelines

### Alert Thresholds

Adjust thresholds based on your environment:

1. **Memory/CPU Thresholds**: Modify the percentage in expressions:
   ```yaml
   # Example: Change memory threshold from 85% to 90%
   expr: ... > 0.90  # Instead of > 0.85
   ```

2. **Timing Windows**: Adjust the duration and rate windows:
   ```yaml
   # Example: Change crash loop detection window
   expr: rate(kube_pod_container_status_restarts_total[10m])  # Instead of [5m]
   ```

### Severity Levels

Default severity levels are:
- **critical**: Immediate action required
- **warning**: Investigation needed
- **info**: For awareness

Modify based on your needs:
```yaml
labels:
  severity: warning  # Change to match your alerting policy
```

## 🏥 Health Checks

To verify your alert rules are working:

1. **Prometheus Rules Check**
   ```bash
   curl -s http://prometheus:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type=="alerting")'
   ```

2. **Active Alerts Check**
   ```bash
   curl -s http://prometheus:9090/api/v1/alerts | jq
   ```

3. **Rule Evaluation Time**
   ```bash
   curl -s 'http://prometheus:9090/api/v1/query?query=prometheus_rule_evaluation_duration_seconds'
   ```

## 🔍 Troubleshooting

Common issues and solutions:

1. **No Alerts Firing**
   - Check if Prometheus is receiving metrics
   - Verify rule syntax
   - Check label selectors match your environment

2. **Too Many Alerts**
   - Review threshold values
   - Consider adding inhibition rules
   - Group related alerts

3. **Missing Metrics**
   - Verify exporter deployments
   - Check Prometheus scrape configs
   - Review service/pod annotations

## 🚀 Production Best Practices

1. **Alert Routing**
   ```yaml
   # alertmanager.yml
   routes:
     - match:
         severity: critical
       receiver: pager-duty
     - match:
         severity: warning
       receiver: slack
   ```

2. **Alert Grouping**
   ```yaml
   # alertmanager.yml
   group_by: ['alertname', 'cluster', 'service']
   group_wait: 30s
   group_interval: 5m
   repeat_interval: 4h
   ```

3. **Inhibition Rules**
   ```yaml
   inhibit_rules:
     - source_match:
         severity: 'critical'
       target_match:
         severity: 'warning'
       equal: ['alertname', 'cluster', 'service']
   ```

4. **Recording Rules**
   Create recording rules for complex expressions to improve performance.

## 📚 Additional Resources

1. [Prometheus Operator Documentation](https://prometheus-operator.dev/)
2. [Kubernetes Monitoring Guide](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)
3. [PromQL Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
4. [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
5. [kube-state-metrics Documentation](https://github.com/kubernetes/kube-state-metrics/tree/master/docs)
