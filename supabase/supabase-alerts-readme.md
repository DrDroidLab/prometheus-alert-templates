# Supabase Prometheus Alert Templates

This document provides detailed information about Supabase Prometheus alert templates and how to set them up in your environment. Since Supabase is built on top of PostgreSQL and includes additional services, these alerts cover both the core database and Supabase-specific components.

## Prerequisites

- Prometheus server (v2.x or higher)
- Supabase instance (self-hosted or cloud)
- PostgreSQL exporter (for database metrics)
- Node exporter (for host metrics)

## Setup Instructions

### 1. Configure Supabase Metrics

For self-hosted Supabase, ensure metrics are enabled in your configuration:

```yaml
services:
  kong:
    environment:
      KONG_VITALS: on
      KONG_VITALS_STRATEGY: prometheus
  
  postgrest:
    environment:
      PGRST_METRICS: true
  
  gotrue:
    environment:
      GOTRUE_METRICS_ENABLED: true
```

### 2. Configure Prometheus

Add the following jobs to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'supabase'
    static_configs:
      - targets: ['localhost:8080']  # Supabase API
    metrics_path: /metrics

  - job_name: 'supabase-postgres'
    static_configs:
      - targets: ['localhost:9187']  # PostgreSQL metrics
    metrics_path: /metrics

  - job_name: 'supabase-kong'
    static_configs:
      - targets: ['localhost:8001']  # Kong metrics
    metrics_path: /metrics
```

### 3. Import Alert Rules

Copy the alert rules from `supabase-prometheus-alerts-template.yaml` to your Prometheus rules directory and reload Prometheus.

## Alert Rules Explanation

### Critical Alerts

1. **SupabaseInstanceDown**
   - Triggers when Supabase instance is down for more than 1 minute
   - Critical severity
   - Immediate action required

2. **SupabaseDiskSpaceCritical**
   - Triggers when disk space usage exceeds 85%
   - Critical severity
   - Action required to prevent service outage

### Warning Alerts

1. **SupabaseHighConnections**
   - Monitors database connection usage (>80% of max_connections)
   - Indicates potential connection pool exhaustion
   - Consider connection pooling or increasing limits

2. **SupabaseAuthFailures**
   - Monitors authentication failures
   - Helps detect potential security issues
   - Review auth logs and access patterns

3. **SupabaseStorageErrors**
   - Monitors storage service errors
   - Indicates potential storage issues
   - Check storage configuration and permissions

4. **SupabaseRealtimeConnections**
   - Monitors realtime connection count
   - Helps manage websocket connections
   - Consider scaling if consistently high

5. **SupabaseEdgeFunctionErrors**
   - Monitors Edge Function execution errors
   - Review function logs and performance
   - Check for resource constraints

6. **SupabaseHighLatency**
   - Monitors API response times
   - Indicates performance issues
   - Review query performance and resource usage

7. **SupabasePostgRESTErrors**
   - Monitors PostgREST API errors
   - Check API configuration and access patterns
   - Review database performance

8. **SupabaseGotTrueErrors**
   - Monitors authentication service errors
   - Review auth service logs
   - Check external auth provider connectivity

## Recommended Thresholds

The alert thresholds are based on general best practices but may need adjustment:

- Auth failures: 10 per 5 minutes
- Storage errors: 5 per 5 minutes
- Edge Function errors: 5 per 5 minutes
- API latency: 1 second average
- Disk space warning: 85%
- CPU usage warning: 80%
- Realtime connections: 1000
- PostgREST/GoTrue errors: 5 per 5 minutes

## Tuning Recommendations

1. **Database Performance**
   - Regular PostgreSQL maintenance
   - Index optimization
   - Connection pooling configuration

2. **API Performance**
   - PostgREST query optimization
   - API rate limiting configuration
   - Cache strategy implementation

3. **Authentication Service**
   - JWT token configuration
   - External provider settings
   - Rate limiting configuration

## Grafana Integration

Recommended Grafana dashboard panels:

1. API Performance
   - Request rates
   - Response times
   - Error rates

2. Database Metrics
   - Connection pools
   - Query performance
   - Resource usage

3. Auth Service
   - Authentication rates
   - Error rates
   - Active sessions

4. Storage Service
   - Upload/download rates
   - Error rates
   - Storage usage

5. Edge Functions
   - Execution times
   - Error rates
   - Resource usage

## Troubleshooting

### Common Issues

1. **API Performance Issues**
   - Check PostgREST logs
   - Review database performance
   - Monitor Kong gateway metrics

2. **Authentication Problems**
   - Verify GoTrue configuration
   - Check external auth providers
   - Review rate limits

3. **Storage Service Issues**
   - Check storage permissions
   - Verify bucket configuration
   - Monitor storage capacity

4. **Edge Function Problems**
   - Review function logs
   - Check resource limits
   - Monitor execution times

## Security Considerations

1. **Authentication**
   - Monitor failed login attempts
   - Review JWT configuration
   - Regular security audits

2. **API Security**
   - Review RLS policies
   - Monitor unauthorized access
   - Check API rate limits

3. **Storage Security**
   - Review bucket policies
   - Monitor file access patterns
   - Check file type restrictions

## Backup and Recovery

1. **Database Backups**
   - Regular backup schedule
   - Backup verification
   - Recovery testing

2. **Configuration Backups**
   - Service configurations
   - Security settings
   - Custom functions

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgREST Documentation](https://postgrest.org/)
- [GoTrue Documentation](https://github.com/supabase/gotrue)

## Support

For issues with these alert templates:
1. Verify metrics collection is working
2. Check individual service logs
3. Review alert conditions and thresholds
4. Adjust based on your environment's needs

## Best Practices

1. **Monitoring Strategy**
   - Regular threshold review
   - Alert response procedures
   - Escalation paths

2. **Performance Optimization**
   - Regular performance reviews
   - Resource scaling plans
   - Optimization strategies

3. **Security Monitoring**
   - Regular security audits
   - Access pattern review
   - Security update procedures 