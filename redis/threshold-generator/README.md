# Redis Threshold Generator

A machine learning-based tool that automatically generates intelligent alert thresholds for Redis monitoring metrics. The tool analyzes historical data from Prometheus to determine appropriate warning and critical thresholds for various Redis metrics.

## Features

- Automatically analyzes historical Redis metrics data
- Uses machine learning to detect anomalies and outliers
- Generates warning and critical thresholds for multiple Redis metrics:
  - Memory usage
  - Connected clients
  - Rejected connections
  - Slow queries
  - Command latency
  - Evicted keys
  - CPU usage
  - Hit rate
  - Network I/O
  - Replication lag
- Outputs Prometheus-compatible alert rules
- Includes detailed analysis reports

## Requirements

- Python 3.6+
- Prometheus instance with Redis metrics
- Required Python packages (install via `pip install -r redis/threshold-generator/requirements.txt`):
  - numpy
  - pandas
  - scipy
  - scikit-learn
  - PyYAML
  - requests

## Configuration

Modify the configuration file at `redis/threshold-generator/config.yaml` to point to your Prometheus instance:

```yaml
prometheus:
  url: "http://your-prometheus-url"
```

## Usage

Run the threshold generator with:

```bash
python redis/threshold-generator/ml-generator.py --config redis/threshold-generator/config.yaml
```

### Output

The tool generates two files in a timestamped directory under `redis/threshold-generator/Output/`:

1. `redis_thresholds_[timestamp].yaml`: Prometheus alert rules with generated thresholds
2. `threshold_analysis_[timestamp].json`: Detailed analysis of the metrics and threshold calculations

## How It Works

1. Collects historical data from Prometheus for each Redis metric
2. Performs statistical analysis on the data
3. Uses machine learning algorithms (Isolation Forest and DBSCAN) to detect anomalies
4. Generates appropriate warning and critical thresholds based on:
   - Statistical measures (mean, standard deviation)
   - Percentiles (p95, p99)
   - Anomaly detection results
5. Creates Prometheus alert rules with the calculated thresholds

## Alert Rules

The generated alert rules follow Prometheus best practices:

- Warning alerts trigger after 5 minutes
- Critical alerts trigger after 2 minutes
- Each alert includes:
  - Clear description
  - Current value and threshold
  - Appropriate severity level
  - Metric-specific labels

## 📊 Customizing Metrics

You can extend the monitoring by adding more metrics to the `self.default_metrics` dictionary in the ML generator. This allows you to monitor additional Redis metrics that are important for your specific use case:

```python
self.default_metrics = {
    # Existing metrics
    'memory_usage': 'redis_memory_used_bytes',
    'connected_clients': 'redis_connected_clients',

    # Add your custom metrics here
    'custom_metric_1': 'redis_your_custom_metric',
    'custom_metric_2': 'redis_another_metric',

    # Example of a derived metric
    'cache_hit_ratio': 'rate(redis_keyspace_hits_total[5m]) / rate(redis_keyspace_misses_total[5m])'
}
```

When adding new metrics:

1. Ensure the metric name matches exactly what's exposed by Redis Exporter
2. Add appropriate alert types and directions for your new metrics

## Interactive Analysis

You can also use our interactive Colab notebook to visualize your Redis metrics and thresholds:
[Open in Colab](https://colab.research.google.com/drive/1Xm-kS2_HFcwuCRxkFG9Qf8lyb7qJQJI3?usp=sharing)

The notebook allows you to:

- Upload your alert.yaml file
- Visualize metric data with interactive plots
- Analyze threshold effectiveness
- Generate custom visualizations
