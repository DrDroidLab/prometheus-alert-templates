#!/usr/bin/env python3
"""
ML-Based Threshold Generator for Redis Monitoring Alerts
Analyzes historical data from Prometheus to generate intelligent thresholds
"""

import yaml
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import logging
import json
import os
from typing import Dict, List, Any
import requests
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedisThresholdGenerator:
    def __init__(self, config_file: str):
        """Initialize the threshold generator with configuration"""
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.lookback_days = self.config.get('lookback_days', 28)  # 4 weeks default
        self.prometheus_url = self.config['prometheus']['url'].rstrip('/')
        
        # Default metric definitions with their PromQL queries
        self.default_metrics = {
            'memory_usage_percent': {
                'query': '(redis_memory_used_bytes / redis_memory_max_bytes) * 100',
                'type': 'percentage',
                'direction': 'upper'
            },
            'connected_clients': {
                'query': 'redis_connected_clients',
                'type': 'count',
                'direction': 'upper'
            },  
            'rejected_connections': {
                'query': 'increase(redis_rejected_connections_total[5m])',
                'type': 'rate',
                'direction': 'upper'
            },
            'slow_queries': {
                'query': 'increase(redis_slowlog_length[5m])',
                'type': 'rate',
                'direction': 'upper'
            },
            'command_latency': {
                'query': 'redis_command_duration_seconds_total / redis_commands_processed_total',
                'type': 'duration',
                'direction': 'upper'
            },
            'evicted_keys': {
                'query': 'increase(redis_evicted_keys_total[5m])',
                'type': 'rate',
                'direction': 'upper'
            },
            'cpu_usage': {
                'query': 'redis_cpu_sys_seconds_total + redis_cpu_user_seconds_total',
                'type': 'duration',
                'direction': 'upper'
            },
            'hit_rate': {
                'query': '(redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)) * 100',
                'type': 'percentage',
                'direction': 'lower'
            },
            'network_io': {
                'query': 'rate(redis_net_input_bytes_total[5m]) + rate(redis_net_output_bytes_total[5m])',
                'type': 'bytes',
                'direction': 'upper'
            },
            'replication_lag': {
                'query': 'redis_master_repl_offset - redis_slave_repl_offset',
                'type': 'bytes',
                'direction': 'upper'
            }
        }

    def query_prometheus(self, query: str, hours: int = None) -> List[Dict]:
        """
        Query Prometheus for metric data.
        If hours is None, uses the configured lookback_days.
        If hours is 0, performs an instant query.
        Returns list of dicts: [{'timestamp': ..., 'value': ...}, ...]
        """
        try:
            if hours == 0:
                # Instant query
                url = f"{self.prometheus_url}/api/v1/query"
                params = {'query': query}
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        data = result.get('data', {})
                        if data.get('resultType') == 'vector' and data.get('result'):
                            results = []
                            for item in data['result']:
                                if 'value' in item and len(item['value']) == 2:
                                    timestamp = datetime.utcfromtimestamp(float(item['value'][0]))
                                    value = float(item['value'][1]) if item['value'][1] != 'NaN' else None
                                    if value is not None and math.isfinite(value):
                                        results.append({'timestamp': timestamp, 'value': value})
                            return results
                return []
            
            # Range query
            end = datetime.utcnow()
            if hours:
                start = end - timedelta(hours=hours)
                step = '60s'  # 1 minute for short queries
            else:
                start = end - timedelta(days=self.lookback_days)
                step = '5m'   # 5 minutes for long queries
            
            url = f"{self.prometheus_url}/api/v1/query_range"
            params = {
                'query': query,
                'start': start.timestamp(),
                'end': end.timestamp(),
                'step': step
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    data = result.get('data', {})
                    if data.get('resultType') == 'matrix' and data.get('result'):
                        results = []
                        for series in data['result']:
                            if 'values' in series:
                                for value_pair in series['values']:
                                    if len(value_pair) == 2:
                                        timestamp = datetime.utcfromtimestamp(float(value_pair[0]))
                                        try:
                                            value = float(value_pair[1])
                                            if math.isfinite(value):
                                                results.append({'timestamp': timestamp, 'value': value})
                                        except (ValueError, TypeError):
                                            continue
                        return results
            
            return []
            
        except Exception as e:
            logger.debug(f"Error querying Prometheus: {e}")
            return []

    def analyze_time_series(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze time series data and extract statistical features"""
        if not data:
            return {}
        
        values = [point['value'] for point in data]
        
        if len(values) < 3:
            # Insufficient data - use simple estimation
            current_value = values[0] if values else 0
            return {
                'mean': current_value,
                'std': max(current_value * 0.1, 1),
                'min': current_value,
                'max': current_value,
                'p95': current_value * 1.2,
                'p99': current_value * 1.4,
                'data_points': len(values),
                'insufficient_data': True
            }
        
        # Calculate statistics
        stats = {
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99),
            'p90': np.percentile(values, 90),
            'p75': np.percentile(values, 75),
            'p25': np.percentile(values, 25),
            'data_points': len(values)
        }
        
        # Advanced analysis for sufficient data
        if len(values) >= 10:
            try:
                # Outlier detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(np.array(values).reshape(-1, 1))
                stats['has_outliers'] = np.any(outliers == -1)
                
                # Anomaly detection
                if len(values) >= 20:
                    scaler = StandardScaler()
                    scaled_values = scaler.fit_transform(np.array(values).reshape(-1, 1))
                    dbscan = DBSCAN(eps=0.5, min_samples=5)
                    clusters = dbscan.fit_predict(scaled_values)
                    stats['anomaly_detected'] = -1 in clusters
                
            except Exception as e:
                logger.debug(f"Advanced analysis failed: {e}")
        
        return stats

    def generate_thresholds(self, metric_name: str, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Generate warning and critical thresholds based on analysis"""
        if not analysis:
            return {'warning': 0, 'critical': 0}
        
        metric_config = self.default_metrics.get(metric_name, {'direction': 'upper', 'type': 'count'})
        direction = metric_config['direction']
        metric_type = metric_config['type']
        
        # Calculate thresholds based on statistics
        mean = analysis['mean']
        std = analysis['std']
        p95 = analysis['p95']
        p99 = analysis['p99']
        
        if direction == 'upper':
            if metric_type == 'percentage':
                warning = min(85, max(mean + 2 * std, p95))
                critical = min(95, max(mean + 3 * std, p99))
            elif metric_type == 'ratio':
                warning = max(mean + 2 * std, p95, 2.0)  # Minimum threshold for ratios
                critical = max(mean + 3 * std, p99, 3.0)
            elif metric_type == 'duration':
                warning = min(1.0, max(mean + 2 * std, p95))
                critical = min(5.0, max(mean + 3 * std, p99))
            else:
                warning = max(mean + 2 * std, p95)
                critical = max(mean + 3 * std, p99)
        else:
            # For metrics where lower values are bad
            warning = max(70, mean - 2 * std)
            critical = max(50, mean - 3 * std)
        
        return {
            'warning': round(max(warning, 0), 2),
            'critical': round(max(critical, 0), 2)
        }

    def generate_alert_rules(self, thresholds: Dict[str, Dict[str, float]]) -> Dict:
        """Generate Prometheus alert rules YAML"""
        alert_rules = {
            'groups': [{
                'name': 'redis_ml_generated_alerts',
                'rules': []
            }]
        }
        
        # Generate rules for each metric
        for metric_name, threshold_data in thresholds.items():
            if metric_name not in self.default_metrics:
                continue
                
            metric_config = self.default_metrics[metric_name]
            query = metric_config['query']
            direction = metric_config['direction']
            
            for severity, threshold_value in threshold_data.items():
                operator = '<' if direction == 'lower' else '>'
                
                rule = {
                    'alert': f"Redis_{metric_name.title().replace('_', '')}_{severity.title()}",
                    'expr': f"{query} {operator} {threshold_value}".replace('\n', ' ').strip(),
                    'for': '5m' if severity == 'warning' else '2m',
                    'labels': {
                        'severity': severity,
                        'service': 'redis',
                        'metric': metric_name
                    },
                    'annotations': {
                        'summary': f"Redis {metric_name.replace('_', ' ')} {severity} threshold exceeded",
                        'description': f"Redis {metric_name.replace('_', ' ')} is {{{{ $value }}}} (threshold: {threshold_value})"
                    }
                }
                alert_rules['groups'][0]['rules'].append(rule)
        
        return alert_rules

    def run(self) -> Dict:
        """Main execution function"""
        logger.info("Starting ML-based threshold generation for Redis metrics")
        
        all_thresholds = {}
        analysis_results = {}
        
        # Process each metric
        for metric_name, metric_config in self.default_metrics.items():
            logger.info(f"Processing metric: {metric_name}")
            
            # Query data with fallback strategy
            data = self.query_prometheus(metric_config['query'])
            if not data:
                logger.info(f"No historical data, trying 1-hour window for {metric_name}")
                data = self.query_prometheus(metric_config['query'], hours=1)
            if not data:
                logger.info(f"No recent data, trying instant query for {metric_name}")
                data = self.query_prometheus(metric_config['query'], hours=0)
            
            # Analyze and generate thresholds
            analysis = self.analyze_time_series(data)
            analysis_results[metric_name] = analysis
            
            thresholds = self.generate_thresholds(metric_name, analysis)
            all_thresholds[metric_name] = thresholds
            
            logger.info(f"Generated thresholds for {metric_name}: {thresholds}")
        
        # Generate alert rules
        alert_rules = self.generate_alert_rules(all_thresholds)
        
        # Save results
        self._save_results(all_thresholds, analysis_results, alert_rules)
        
        return {
            'thresholds': all_thresholds,
            'alert_rules': alert_rules,
            'analysis': analysis_results
        }

    def _save_results(self, thresholds: Dict, analysis: Dict, alert_rules: Dict):
        """Save results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f'redis/threshold-generator/Output/{timestamp}'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save alert rules with custom YAML configuration
        with open(f'{output_dir}/redis_thresholds_{timestamp}.yaml', 'w') as f:
            yaml.dump(alert_rules, f, 
                     default_flow_style=False,
                     width=float("inf"),  # Prevent line wrapping
                     default_style=None,  # Use default style for strings
                     sort_keys=False)     # Preserve order
        
        # Save analysis report
        with open(f'{output_dir}/threshold_analysis_{timestamp}.json', 'w') as f:
            json.dump({
                'thresholds': thresholds,
                'analysis': analysis,
                'working_metrics': {name: config['query'] for name, config in self.default_metrics.items()},
                'generated_at': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        logger.info(f"Results saved to {output_dir}/")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ML-based thresholds for Redis monitoring')
    parser.add_argument('--config', required=True, help='Configuration file path')
    parser.add_argument('--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    try:
        generator = RedisThresholdGenerator(args.config)
        results = generator.run()
        
        if 'error' not in results:
            if args.output:
                with open(args.output, 'w') as f:
                    yaml.dump(results['alert_rules'], f, default_flow_style=False)
                logger.info(f"Alert rules saved to {args.output}")
            
            print("✅ Threshold generation completed successfully!")
        else:
            print(f"❌ Error: {results['error']}")
            
    except Exception as e:
        logger.error(f"Error generating thresholds: {e}")
        raise

if __name__ == "__main__":
    main()