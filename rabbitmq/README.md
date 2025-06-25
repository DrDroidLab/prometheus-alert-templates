# RabbitMQ Alert Rules for Prometheus

This repository provides production-ready RabbitMQ monitoring alert rules for Prometheus. These alerts are designed to work with RabbitMQ's built-in Prometheus plugin (`rabbitmq_prometheus`), which is the recommended way to collect metrics from RabbitMQ 3.8 and later.

## 🔌 Built-in Prometheus Plugin

RabbitMQ comes with a built-in Prometheus plugin that exposes metrics on port 15692. This is now the official and recommended way to collect metrics from RabbitMQ, replacing the older community plugins.

To enable the plugin:
```bash
rabbitmq-plugins enable rabbitmq_prometheus
```

## 🚨 Alert Rules Included

### Node Health & Resource Alarms

| Alert                    | Condition                                                  | Severity | Duration | Purpose                                                              |
|-------------------------|------------------------------------------------------------| -------- | -------- | -------------------------------------------------------------------- |
| **RabbitMQFileDescriptorAlarm** | `rabbitmq_alarms_file_descriptor_limit > 0`       | Critical | 0m       | Alerts when file descriptor limit is reached                         |
| **RabbitMQDiskSpaceAlarm** | `rabbitmq_alarms_free_disk_space_watermark > 0`       | Critical | 0m       | Alerts when disk space watermark is reached                         |
| **RabbitMQMemoryAlarm** | `rabbitmq_alarms_memory_used_watermark > 0`              | Critical | 0m       | Alerts when memory watermark is reached                             |
| **RabbitMQHighMemoryUsage** | Memory usage > 80% of available                       | Warning  | 5m       | Early warning for memory issues                                      |
| **RabbitMQLowDiskSpace** | `rabbitmq_disk_space_available_bytes < 10GB`            | Warning  | 5m       | Early warning for disk space issues                                  |

### Resource Usage

| Alert                          | Condition                                            | Severity | Duration | Purpose                                                              |
|-------------------------------|------------------------------------------------------| -------- | -------- | -------------------------------------------------------------------- |
| **RabbitMQHighFileDescriptorUsage** | File descriptor usage > 80%                   | Warning  | 5m       | Alerts when file descriptors are being depleted                      |
| **RabbitMQHighSocketUsage** | TCP socket usage > 80%                                | Warning  | 5m       | Alerts when TCP sockets are being depleted                           |
| **RabbitMQHighErlangProcessUsage** | `erlang_processes_used > 950000`              | Warning  | 5m       | Alerts when too many Erlang processes are being used                 |

### Connection and Channel Health

| Alert                    | Condition                                                  | Severity | Duration | Purpose                                                              |
|-------------------------|------------------------------------------------------------| -------- | -------- | -------------------------------------------------------------------- |
| **RabbitMQHighConnectionChurn** | High rate of connections opened/closed             | Warning  | 5m       | Detects unstable client behavior with connection cycling             |
| **RabbitMQHighChannelChurn** | High rate of channels opened/closed                  | Warning  | 5m       | Detects unstable client behavior with channel cycling                |
| **RabbitMQHighQueueChurn** | High rate of queue creation/deletion                   | Warning  | 5m       | Detects potential queue lifecycle issues                             |

## 📊 Metrics Collection

The built-in Prometheus plugin exposes metrics through several endpoints:

- `/metrics` (port 15692) - Basic metrics about:
  - Node status and alarms
  - Resource usage (memory, disk, file descriptors)
  - Connection and channel counts
  - Queue statistics
  - Runtime metrics

## 🔧 Integration Methods

### Docker Compose Setup

```yaml
rabbitmq:
  image: rabbitmq:3.12-management
  hostname: rabbitmq
  ports:
    - "5672:5672"   # AMQP protocol
    - "15672:15672" # Management UI
    - "15692:15692" # Prometheus metrics
  environment:
    - RABBITMQ_DEFAULT_USER=guest
    - RABBITMQ_DEFAULT_PASS=guest
  command: >
    bash -c "rabbitmq-plugins enable rabbitmq_prometheus &&
             docker-entrypoint.sh rabbitmq-server"
```

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15692']
    metrics_path: /metrics
    scrape_interval: 15s
```

## ⚙️ Plugin Configuration

The Prometheus plugin can be configured in `rabbitmq.conf`:

```ini
# Enable Prometheus metrics
prometheus.return_per_object_metrics = true

# Metrics endpoints
management.prometheus.path = /metrics
management.prometheus.port = 15692

# TLS configuration (optional)
prometheus.ssl.port = 15691
prometheus.ssl.cacertfile = /path/to/ca_certificate.pem
prometheus.ssl.certfile = /path/to/server_certificate.pem
prometheus.ssl.keyfile = /path/to/server_key.pem
```

For more information about RabbitMQ's built-in Prometheus support, see the [official documentation](https://www.rabbitmq.com/prometheus.html). 