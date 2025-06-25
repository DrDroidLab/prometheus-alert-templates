# Airflow Monitoring with Prometheus

This directory contains Prometheus alert rules for monitoring Apache Airflow using its native StatsD metrics support.

## Overview

The monitoring setup uses Airflow's built-in StatsD metrics capabilities along with the official `prom/statsd-exporter` to expose these metrics to Prometheus. This approach leverages Airflow's core metrics system that tracks various aspects including:

- Scheduler performance and health
- Executor resource utilization
- Pool capacity and usage
- DAG processing statistics
- Task execution metrics

## Architecture

The monitoring stack consists of:

1. **Airflow** - Configured to emit StatsD metrics
2. **StatsD Exporter** - Converts StatsD metrics to Prometheus format
3. **Prometheus** - Scrapes and stores metrics
4. **Alertmanager** - Handles alert notifications

## Available Metrics

The alert templates use the following core Airflow metrics:

### Scheduler Metrics
- `airflow_scheduler_heartbeat` - Scheduler health indicator
- `airflow_scheduler_scheduler_loop_duration` - Time taken for scheduler loops
- `airflow_scheduler_critical_section_duration` - Duration of critical operations
- `airflow_scheduler_tasks_starving` - Tasks unable to be scheduled
- `airflow_scheduler_tasks_executable` - Tasks ready for execution

### Executor Metrics
- `airflow_executor_open_slots` - Available execution slots
- `airflow_executor_queued_tasks` - Tasks waiting to be executed
- `airflow_executor_running_tasks` - Currently running tasks

### Pool Metrics
- `airflow_pool_open_slots` - Available slots in pools
- `airflow_pool_running_slots` - Used slots in pools
- `airflow_pool_queued_slots` - Tasks queued in pools
- `airflow_pool_deferred_slots` - Deferred tasks in pools

### DAG Processing Metrics
- `airflow_dag_processing_file_path_queue_size` - Files waiting to be processed
- `airflow_dag_processing_import_errors` - DAG import failure count
- `airflow_dag_processing_total_parse_time` - Time spent parsing DAGs
- `airflow_dagbag_size` - Total number of DAGs

## Alert Rules

The `airflow-prometheus-alerts-template.yaml` file contains alert rules for:

1. **Scheduler Health**
   - Scheduler heartbeat monitoring
   - Scheduler loop performance
   - Critical section duration

2. **Resource Utilization**
   - Executor slot availability
   - Pool capacity monitoring
   - Task starvation detection

3. **Task Execution**
   - Queue size monitoring
   - Execution bottleneck detection

4. **DAG Processing**
   - Import error detection
   - Processing queue monitoring

## Setup

1. Ensure Airflow is configured with StatsD metrics enabled:
   ```yaml
   AIRFLOW__METRICS__STATSD_ON: "True"
   AIRFLOW__METRICS__STATSD_HOST: "statsd"
   AIRFLOW__METRICS__STATSD_PORT: "9125"
   AIRFLOW__METRICS__STATSD_PREFIX: "airflow"
   ```

2. Deploy the StatsD exporter:
   ```yaml
   statsd:
     image: prom/statsd-exporter:latest
     ports:
       - "9125:9125/udp"
       - "9102:9102"
   ```

3. Configure Prometheus to scrape the StatsD exporter:
   ```yaml
   - job_name: 'airflow'
     static_configs:
       - targets: ['statsd:9102']
     metrics_path: '/metrics'
   ```

## Alert Customization

The alert thresholds are based on general recommendations but should be adjusted according to your specific needs. Consider:

- Your DAG execution patterns
- Available executor resources
- Pool configurations
- Processing queue patterns

## Metric Labels

The alerts use various labels provided by Airflow's metrics:

- `pool_name`: The name of the resource pool
- Other labels vary by metric type

## Contributing

Feel free to submit issues, fork the repository and create pull requests for any improvements. 