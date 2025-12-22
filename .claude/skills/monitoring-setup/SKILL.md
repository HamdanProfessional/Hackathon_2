---
name: monitoring-setup
description: Monitoring and observability setup skills for Prometheus, Grafana, alerting, and logging. Use when setting up application monitoring, creating dashboards, configuring alerts, implementing distributed tracing, or establishing observability for Kubernetes deployments. Essential for Phase V production monitoring.
---

# Monitoring and Observability Setup

This skill provides guidance for setting up comprehensive monitoring with Prometheus, Grafana, and alerting.

## When to Use This Skill

Use this skill when:
- Installing Prometheus on Kubernetes
- Creating Grafana dashboards
- Configuring alert rules
- Setting up ServiceMonitors
- Implementing application metrics
- Troubleshooting monitoring issues

## Quick Reference

### Prometheus Commands

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Prometheus
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80
```

### Grafana Commands

```bash
# Default credentials
username: admin
password: prom-operator

# Login to Grafana
open http://localhost:3000

# Get Grafana password
kubectl get secret prometheus-grafana -o jsonpath='{.data.admin-password}' | base64 -d
```

## Prometheus Installation

### Install via Helm

```bash
# Install kube-prometheus-stack (includes Prometheus, Grafana, AlertManager)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123
```

### Custom Values

```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    retention: 15d
    retentionSize: 50GB
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: standard
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

grafana:
  persistence:
    enabled: true
    size: 10Gi
  adminPassword: admin123
```

## ServiceMonitors

### Application ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
  labels:
    app: todo-backend
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
```

### Deploy ServiceMonitor

```bash
kubectl apply -f k8s/monitoring/servicemonitor-backend.yaml

# Verify
kubectl get servicemonitor
kubectl describe servicemonitor backend-monitor
```

## Application Metrics

### FastAPI Metrics

```python
# Install prometheus-client
# pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

app = FastAPI()

# Expose metrics at /metrics endpoint
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Custom Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
task_created_counter = Counter('tasks_created_total', 'Total tasks created')
task_completion_duration = Histogram('task_completion_seconds', 'Task completion duration')
active_tasks_gauge = Gauge('active_tasks_total', 'Number of active tasks')

# Use metrics
task_created_counter.inc()

with task_completion_duration.time():
    # do work
    pass

active_tasks_gauge.set(count)
```

### Python Metrics

```python
from prometheus_client import Counter, start_http_server

# Create counter
request_counter = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])

# Increment
request_counter.labels(method='GET', endpoint='/api/tasks').inc()

# Start metrics server
start_http_server(8000)
```

## Grafana Dashboards

### Import Dashboard

1. Open Grafana: http://localhost:3000
2. Click + → Import
3. Enter dashboard ID or upload JSON
4. Select Prometheus data source
5. Click Import

### Recommended Dashboards

| ID | Name | Purpose |
|----|------|---------|
| 7249 | Kubernetes Cluster Monitoring | Cluster overview |
| 7362 | Node Exporter Full | Node metrics |
| 14531 | Kubernetes Pod Monitoring | Pod metrics |
| 10826 | Dapr Metrics | Dapr sidecar metrics |
| 14675 | FastAPI | Application metrics |

### Create Custom Dashboard

```json
{
  "dashboard": {
    "title": "Todo App Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Active Tasks",
        "targets": [
          {
            "expr": "active_tasks_total"
          }
        ]
      }
    ]
  }
}
```

## Alert Rules

### PrometheusRule

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  labels:
    app: todo-app
spec:
  groups:
  - name: todo-app.rules
    rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status="500"}[5m]) > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors/sec"

  - alert: PodNotReady
    expr: kube_pod_status_phase{phase!="Running"} > 0
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "Pod not ready"
      description: "Pod {{ $labels.pod }} is not ready"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Container {{ $labels.container }} using >90% memory"
```

### Deploy Alert Rules

```bash
kubectl apply -f k8s/monitoring/prometheus-rules.yaml

# Verify rules loaded
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
open http://localhost:9090/alerts
```

## AlertManager

### Configure AlertManager

```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
    route:
      group_by: ['alertname', 'cluster']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'default'
      routes:
      - match:
          severity: critical
        receiver: 'pagerduty'
    receivers:
    - name: 'default'
      email_configs:
      - to: 'alerts@example.com'
    - name: 'pagerduty'
      pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY'
```

## Logging

### Loki Installation

```bash
# Add Loki Helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --create-namespace
```

### Fluent Bit Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         1
        Daemon        off
        Log_Level     info

    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token

    [OUTPUT]
        Name            loki
        Match           *
        Url             http://loki:3100/loki/api/v1/push
        Batch          true
        BatchWait      1
        BatchSize      100
        Labels         job=fluent-bit
```

## Distributed Tracing

### Tempo Installation

```bash
# Install Tempo (Grafana Tracing)
helm install tempo grafana/tempo \
  --namespace monitoring \
  --create-namespace
```

### OpenTelemetry in Python

```bash
# Install OpenTelemetry
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()
trace_exporter = OTLPSpanExporter(endpoint="http://tempo:4317")
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

## Dashboards for Todo App

### Backend Metrics

| Panel | Query |
|-------|-------|
| Request Rate | `rate(http_requests_total{app="todo-backend"}[5m])` |
| Error Rate | `rate(http_requests_total{app="todo-backend",status="500"}[5m])` |
| Response Time | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| Active Connections | `http_active_connections` |

### Database Metrics

| Panel | Query |
|-------|-------|
| Connection Pool | `pg_stat_activity_count{datname="neondb"}` |
| Query Duration | `rate(pg_stat_statements_mean_time_ms[5m])` |
| Transactions | `rate(xact_commit[5m])` |

### Dapr Metrics

| Panel | Query |
|-------|-------|
| Sidecar Health | `up{job="dapr-sidecar-injector"}` |
| Request Rate | `rate(dapr_http_server_sent_requests{app_id="todo-backend"}[5m])` |
| Request Latency | `histogram_quantile(0.95, rate(dapr_http_server_sent_latency_bucket[5m]))` |

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check ServiceMonitor
kubectl get servicemonitor

# Check targets in Prometheus UI
open http://localhost:9090/targets

# Check endpoints
kubectl get endpoints backend-monitor

# Verify metrics endpoint
kubectl run -it --rm curl --image=curlimages/curl --restart=Never \
  -- curl http://backend-service:8000/metrics
```

### Grafana Data Source Issues

```bash
# Check Prometheus service
kubectl get svc prometheus-kube-prometheus-prometheus

# Port forward to access
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

# Test in Grafana
# Configuration > Data Sources > Prometheus
# URL: http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
```

### Alerts Not Firing

```bash
# Check AlertManager
kubectl get prometheus prometheus-kube-prometheus-alertmanager -o yaml

# View alert rules
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
open http://localhost:9090/alerts

# Check rule evaluation
open http://localhost:9090/graph?g0.expr=alert_name
```

## Best Practices

### Metric Naming

```python
# Good: Descriptive names
task_creation_duration_seconds
task_completion_total
active_tasks_count

# Avoid: Generic names
duration
count
time
```

### Label Strategy

```python
# Always include useful labels
task_created_total.labels(
    user_id=str(user.id),
    priority=task.priority,
    has_due_date=task.due_date is not None
).inc()
```

### Dashboard Organization

1. **Overview Dashboard**: High-level metrics for all services
2. **Service Dashboards**: Detailed metrics per service
3. **Resource Dashboards**: Cluster and node metrics
4. **Alert Dashboard**: Active and resolved alerts

## For More Information

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Monitoring](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
