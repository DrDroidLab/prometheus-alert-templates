# Apache Kafka Alert Rules for Prometheus

This repository provides a set of production-ready alert rules for monitoring Apache Kafka with Prometheus. These rules are designed to work with a JMX exporter that exposes Kafka's internal metrics.

The JMX exporter configuration used as a base for these alerts can be found in the `oded-dd/prometheus-jmx-kafka` repository. We extend our gratitude to the contributors of that repository for providing a comprehensive starting point.

## 🚨 Alert Rules Included

### Broker Health & Availability

| Alert             | Condition                 | Severity | Duration | Purpose                                                    |
| ----------------- | ------------------------- | -------- | -------- | ---------------------------------------------------------- |
| **KafkaBrokerDown** | `up{job=~".*kafka.*"} == 0` | Critical | 1m       | Immediate notification when a Kafka broker is unreachable. |
| **KafkaNoActiveController** | `sum(kafka_controller_active_controller_count) == 0` | Critical | 1m       | Alerts when there is no active controller in the Kafka cluster. |

### Cluster State & Partition Health

| Alert                           | Condition                                                                | Severity | Duration | Purpose                                                                            |
| ------------------------------- | ------------------------------------------------------------------------ | -------- | -------- | ---------------------------------------------------------------------------------- |
| **KafkaUnderReplicatedPartitions**  | `kafka_server_under_replicated_partitions > 0`              | Critical | 5m       | Detects partitions with fewer replicas than configured, indicating potential data loss risk. |
| **KafkaOfflinePartitions**      | `kafka_controller_offline_partitions_count > 0`       | Critical | 5m       | Notifies when partitions are offline and unavailable for reads/writes.             |

### Performance & Latency

| Alert                       | Condition                               | Severity | Duration | Purpose                                                                                  |
| --------------------------- | --------------------------------------- | -------- | -------- | ---------------------------------------------------------------------------------------- |
| **KafkaHighRequestLatency**    | `(sum(rate(kafka_network_total_time_ms_total[5m])) by (instance, request) / sum(rate(kafka_network_requests_per_sec[5m])) by (instance, request)) > 1000`          | Warning  | 5m       | Detects when the average request latency is over 1 second.                  |
| **KafkaHighFailedProduceRequests** | `sum(rate(kafka_server_failed_produce_requests_per_sec[5m])) by (instance) > 10` | Warning  | 5m      | Alerts when the rate of failed produce requests is high. |
| **KafkaHighFailedFetchRequests** | `sum(rate(kafka_server_failed_fetch_requests_per_sec[5m])) by (instance) > 10` | Warning  | 5m      | Alerts when the rate of failed fetch requests is high. |


## 📋 Prerequisites

Before integrating these alerts, ensure you have:

1.  **Prometheus** set up for monitoring.
2.  **JMX Exporter** configured as a Java agent for your Kafka brokers. The `kafka-jmx-metric.yml` from `oded-dd/prometheus-jmx-kafka` is recommended.
3.  **Alertmanager** configured to handle alerts.
4.  **Grafana** for visualization (optional).

## 🔧 Integration Methods

The integration process is similar to other services in this repository. You can use these alert rules in a Docker Compose setup, a Kubernetes cluster with `kube-prometheus-stack`, or a vanilla Prometheus setup.

### Scenario 1: Docker Compose Setup

**Step 1: Add alerts directory to your Prometheus volume in `docker-compose.yml`**

```yaml
services:
  prometheus:
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts:/etc/prometheus/alerts
      - prometheus_data:/prometheus
```

**Step 2: Update your `prometheus.yml` to include alert rules**

```yaml
rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: "kafka"
    static_configs:
      - targets: ["kafka:7071"] # Adjust if your exporter is on a different port
```

**Step 3: Copy the alert rules**

```bash
# Copy kafka-prometheus-alerts-template.yaml to your prometheus/alerts/ directory
cp kafka-prometheus-alerts-template.yaml ./prometheus/alerts/kafka.yml

# Restart Prometheus
docker-compose restart prometheus
```

### Scenario 2: Kubernetes with `kube-prometheus-stack`

Update your Helm values to include the Kafka alert rules in `additionalPrometheusRulesMap`.

```yaml
additionalPrometheusRulesMap:
  kafka-alerts:
    groups:
      - name: kafka_alerts
        rules:
          - alert: KafkaBrokerDown
            expr: up{job="kafka"} == 0
            for: 1m
            labels:
              severity: critical
              service: kafka
            annotations:
              summary: "Kafka broker is down"
              description: "Kafka broker {{ $labels.instance }} has been down for more than 1 minute."
        # ... add all other rules from kafka-prometheus-alerts-template.yaml
```

Apply the changes with Helm:

```bash
helm upgrade prometheus-stack prometheus-community/kube-prometheus-stack -f values.yaml -n monitoring
``` 