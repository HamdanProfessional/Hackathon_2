# Agent Monitoring and Health Check Skill

**Type**: Agent Skill
**Category**: Development & Operations
**Phases**: All (especially III+)

---

## Purpose

Monitor AI agent health, performance, and operational metrics to ensure optimal functionality and early detection of issues.

---

## Skill Invocation

```
/skill agent-monitoring action=health-check
/skill agent-monitoring action=performance-metrics
/skill agent-monitoring action=error-analysis
/skill agent-monitoring action=resource-usage
/skill agent-monitoring action=cache-stats
```

---

## What This Skill Does

### 1. Health Check
- Validates agent service connectivity
- Checks database connection health
- Verifies API endpoint availability
- Tests tool execution capabilities
- Reports overall system status

### 2. Performance Metrics
- Collects response time statistics
- Analyzes tool execution performance
- Monitors conversation processing times
- Tracks error rates and success rates
- Provides performance recommendations

### 3. Error Analysis
- Analyzes recent error patterns
- Identifies common failure points
- Categorizes errors by type and frequency
- Suggests improvements based on error data
- Provides error trend analysis

### 4. Resource Usage
- Monitors memory usage patterns
- Tracks database query performance
- Analyzes cache efficiency
- Reports on resource bottlenecks
- Suggests optimization opportunities

### 5. Cache Statistics
- Analyzes cache hit/miss ratios
- Monitors cache memory usage
- Identifies cache optimization opportunities
- Provides cache eviction statistics
- Suggests cache configuration improvements

---

## Success Criteria

✅ All health checks pass without critical failures
✅ Performance metrics collected and analyzed
✅ Error patterns identified and categorized
✅ Resource usage within acceptable thresholds
✅ Cache statistics analyzed and optimized

---

## Deliverables

When this skill completes, you'll have:

1. **Health Report**: Comprehensive system health status
2. **Performance Dashboard**: Key performance indicators and trends
3. **Error Analysis Report**: Error patterns and mitigation strategies
4. **Resource Usage Report**: Resource utilization and recommendations
5. **Cache Optimization Report**: Cache performance and improvement suggestions

---

## Usage Examples

### Basic Health Check
```bash
/skill agent-monitoring action=health-check
```

### Complete Performance Analysis
```bash
/skill agent-monitoring action=performance-metrics duration=24h
```

### Error Investigation
```bash
/skill agent-monitoring action=error-analysis time_range=last-7-days
```

### Resource Monitoring
```bash
/skill agent-monitoring action=resource-usage detailed=true
```

### Cache Analysis
```bash
/skill agent-monitoring action=cache-stats include-recommendations=true
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | Yes | - | Monitoring action to perform |
| duration | string | No | 1h | Time range for metrics (1h, 24h, 7d) |
| time_range | string | No | last-24-hours | Specific time range |
| detailed | boolean | No | false | Include detailed metrics |
| include-recommendations | boolean | No | true | Include optimization suggestions |
| format | string | No | json | Output format (json, table, markdown) |

---

## Implementation Notes

### Health Check Implementation
```python
async def perform_health_check():
    checks = {
        "database": await check_database_health(),
        "api_endpoints": await check_api_endpoints(),
        "tool_execution": await test_tool_execution(),
        "memory_usage": check_memory_usage(),
        "cache_system": await check_cache_health()
    }

    overall_status = "healthy" if all(checks.values()) else "degraded"
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Performance Metrics Collection
```python
async def collect_performance_metrics(duration):
    metrics = {
        "response_times": await get_response_time_stats(duration),
        "tool_performance": await get_tool_performance_stats(),
        "conversation_metrics": await get_conversation_metrics(),
        "error_rates": await calculate_error_rates(duration)
    }

    return analyze_and_format_metrics(metrics)
```

### Error Analysis Implementation
```python
async def analyze_errors(time_range):
    errors = await fetch_error_logs(time_range)

    analysis = {
        "total_errors": len(errors),
        "error_types": categorize_errors(errors),
        "trending_errors": identify_trends(errors),
        "critical_errors": filter_critical_errors(errors),
        "recommendations": generate_error_recommendations(errors)
    }

    return analysis
```

---

## Integration Points

### With Agent Service
- Monitor agent execution times
- Track tool usage patterns
- Analyze conversation flows
- Detect performance bottlenecks

### With Database Layer
- Monitor query performance
- Track connection pool usage
- Analyze query patterns
- Identify slow queries

### With Cache Layer
- Monitor hit/miss ratios
- Track memory usage
- Analyze eviction patterns
- Optimize cache strategies

### With Monitoring Systems
- Export metrics to Prometheus/Grafana
- Send alerts on threshold breaches
- Generate periodic health reports
- Integrate with logging systems

---

## Alerting Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Response Time | >2s | >5s | Alert and investigate |
| Error Rate | >5% | >15% | Immediate attention |
| Memory Usage | >80% | >95% | Scale or optimize |
| Cache Hit Rate | <70% | <50% | Review cache strategy |
| Database Query Time | >1s | >3s | Optimize queries |

---

## Troubleshooting Guide

### Common Issues

1. **Agent Not Responding**
   - Check service status
   - Verify API connectivity
   - Review error logs
   - Check resource usage

2. **High Response Times**
   - Analyze tool execution times
   - Check database performance
   - Review cache efficiency
   - Identify bottlenecks

3. **Frequent Errors**
   - Review error patterns
   - Check input validation
   - Verify API configurations
   - Update error handling

4. **Memory Issues**
   - Monitor memory usage
   - Check for memory leaks
   - Optimize data structures
   - Consider scaling

### Recovery Procedures

1. **Service Restart**
2. **Cache Clearing**
3. **Database Connection Reset**
4. **Configuration Rollback**
5. **Emergency Mode Activation**

---

## Security Considerations

- Restrict access to monitoring endpoints
- Sanitize sensitive data in logs
- Use secure authentication
- Implement rate limiting
- Regular security audits

---

## Performance Optimization Tips

1. **Database Optimization**
   - Use connection pooling
   - Optimize queries
   - Add appropriate indexes
   - Monitor query plans

2. **Cache Optimization**
   - Choose appropriate TTL
   - Monitor cache hit rates
   - Implement cache warming
   - Use multi-level caching

3. **Agent Optimization**
   - Batch operations when possible
   - Use async operations
   - Optimize prompt sizes
   - Implement request queuing

---

**Skill Version**: 1.0.0
**Created**: 2025-12-21
**Hackathon Points**: +150 (Monitoring & Observability)
**Phase**: All (especially III+)