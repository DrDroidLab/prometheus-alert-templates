# Prometheus Alert Templates

This repository contains a collection of Prometheus alert templates for various systems and services. Each directory contains specific alert rules and documentation for monitoring different components of your infrastructure.

## Available Templates

- [Kubernetes](./kubernetes/): Alerts for Kubernetes cluster monitoring
- [Redis](./redis/): Alerts for Redis monitoring
- [PostgreSQL](./postgres/): Alerts for PostgreSQL database monitoring
- [MySQL](./mysql/): Alerts for MySQL database monitoring
- [Cassandra](./cassandra/): Alerts for Cassandra database monitoring (via JMX exporter)
- [MongoDB](./mongodb/): Alerts for MongoDB monitoring
- [Supabase](./supabase/): Alerts for Supabase platform monitoring

## Integration Methods

### 1. Kubernetes with kube-prometheus-stack (Prometheus Operator)

#### Option A: Values.yaml Method (Recommended)
Update your existing Helm values:

```yaml
# values.yaml
additionalPrometheusRulesMap:
  custom-alerts.yaml:
    groups:
    - name: custom_alerts
      rules:
      # Copy rules from respective alert template files
      - alert: ExampleAlert
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Example alert"
          description: "Example description"
```

Apply the update:
```bash
helm upgrade prometheus-stack prometheus-community/kube-prometheus-stack \
  -f values.yaml \
  -n monitoring
```

#### Option B: PrometheusRule CRD
Create a separate PrometheusRule resource:

```yaml
# prometheus-rule.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: custom-alerts
  namespace: monitoring
  labels:
    release: prometheus # Match your Prometheus Operator release label
spec:
  groups:
    - name: custom_alerts
      rules:
        # Copy rules from respective alert template files
```

Apply the rule:
```bash
kubectl apply -f prometheus-rule.yaml
```

### 2. Docker Compose Setup

#### Step 1: Add alerts directory to your Prometheus volume
```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts:/etc/prometheus/alerts  # Mount alerts directory
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
```

#### Step 2: Update prometheus.yml
```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts/*.yml"  # Include all alert files

scrape_configs:
  # Your scrape configs here
```

#### Step 3: Copy alert rules
```bash
# Create alerts directory
mkdir -p ./prometheus/alerts

# Copy alert rules
cp <integration>/*-alerts.yml ./prometheus/alerts/

# Restart Prometheus
docker-compose restart prometheus
```

### 3. Kubernetes with Vanilla Prometheus Helm

#### Step 1: Create values.yaml with Alertmanager and Rules
```yaml
# values.yaml
alertmanager:
  enabled: true
  configMapOverrideName: ""
  config:
    global:
      resolve_timeout: 5m
    route:
      group_by: ['alertname', 'severity']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'default-receiver'
    receivers:
    - name: 'default-receiver'
      # Configure your notification channels

server:
  global:
    scrape_interval: 15s
  alerting:
    alertmanagers:
    - static_configs:
      - targets:
        - "prometheus-alertmanager.monitoring.svc.cluster.local:9093"

serverFiles:
  alerts.yml:
    groups:
    - name: custom_alerts
      rules:
      # Copy rules from respective alert template files
```

#### Step 2: Deploy/Upgrade Prometheus
```bash
# First time installation
helm install prometheus prometheus-community/prometheus \
  -f values.yaml \
  -n monitoring \
  --create-namespace

# Upgrading existing installation
helm upgrade prometheus prometheus-community/prometheus \
  -f values.yaml \
  -n monitoring
```

### 4. Vanilla Prometheus Setup

#### Step 1: Create rules directory
```bash
mkdir -p /etc/prometheus/rules
```

#### Step 2: Copy and organize alert rules
```bash
# Copy alert rules to rules directory
cp <integration>/*-alerts.yml /etc/prometheus/rules/
```

#### Step 3: Configure prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  # Your scrape configs here
```

#### Step 4: Reload Prometheus
```bash
curl -X POST http://localhost:9090/-/reload
```

### 5. Grafana Cloud

1. Navigate to Grafana Cloud Portal
2. Go to Prometheus → Rules
3. Click "New Rule"
4. Copy the alert rules from the respective YAML files
5. Set appropriate labels and annotations
6. Save and activate the rules

## Alert Manager Configuration

### Basic Configuration
```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 5m
    route:
      group_by: ['alertname', 'job']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'default'
    receivers:
      - name: 'default'
        # Configure your notification channels
```

### Advanced Configuration with Multiple Receivers
```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 5m
      slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    route:
      receiver: 'default'
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      routes:
      - receiver: 'critical'
        match:
          severity: critical
        group_wait: 10s
        repeat_interval: 1h
      - receiver: 'warnings'
        match:
          severity: warning
    receivers:
    - name: 'default'
      slack_configs:
      - channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    - name: 'critical'
      slack_configs:
      - channel: '#critical-alerts'
        title: 'CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    - name: 'warnings'
      slack_configs:
      - channel: '#warnings'
        title: 'Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Best Practices

1. **Rule Organization**
   - Keep rules organized by component
   - Use consistent naming conventions
   - Group related alerts together

2. **Alert Severity Levels**
   - critical: Immediate action required
   - warning: Investigation needed
   - info: For informational purposes

3. **Labels and Annotations**
   - Use consistent labels across alerts
   - Include detailed descriptions
   - Add runbook links when available

4. **Timing Parameters**
   - Set appropriate 'for' duration
   - Configure group_wait and group_interval
   - Adjust repeat_interval based on urgency

## Testing Alert Rules

1. Using promtool:
```bash
promtool check rules /path/to/rules/*.yml
```

2. Using Prometheus API:
```bash
curl http://localhost:9090/api/v1/rules
```

3. Using Prometheus UI:
- Navigate to Status → Rules
- Check rule evaluation status

## Maintenance and Updates

1. **Regular Review**
   - Review alert thresholds periodically
   - Update rules based on false positives/negatives
   - Keep documentation current

2. **Version Control**
   - Track changes in version control
   - Document significant updates
   - Test changes before deployment

3. **Backup**
   - Backup rule configurations
   - Document custom modifications
   - Maintain change history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.