# Monitoring Stack for Todo Application

## Overview

This directory contains the complete monitoring configuration for the Todo Application deployed on DigitalOcean Kubernetes (DOKS). The monitoring stack includes Prometheus, Grafana, Alertmanager, and custom ServiceMonitors for application metrics.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DOKS Cluster                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Production Namespace                               │   │
│  │                                                      │   │
│  │  ┌──────────────┐  ┌──────────────────┐            │   │
│  │  │todo-backend  │  │todo-notifications│            │   │
│  │  │   :8000      │  │     :8000         │            │   │
│  │  │  /metrics    │  │    /metrics       │            │   │
│  │  └──────┬───────┘  └────────┬─────────┘            │   │
│  │         │                    │                       │   │
│  │         └────────┬───────────┘                       │   │
│  │                  │                                   │   │
│  │         ┌────────▼─────────┐                        │   │
│  │         │ ServiceMonitors  │                        │   │
│  │         └────────┬─────────┘                        │   │
│  └──────────────────┼──────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼──────────────────────────────────┐  │
│  │  Monitoring Namespace                                │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  Prometheus Operator                         │  │  │
│  │  │  - Scrape metrics from ServiceMonitors       │  │  │
│  │  │  - Evaluate alerting rules                   │  │  │
│  │  │  - Send alerts to Alertmanager               │  │  │
│  │  └─────────────────┬────────────────────────────┘  │  │
│  │                    │                                 │  │
│  │  ┌─────────────────▼────────────────────────────┐  │  │
│  │  │  Alertmanager                                │  │  │
│  │  │  - Route alerts based on severity             │  │  │
│  │  │  - Deduplicate alerts                         │  │  │
│  │  │  - Send notifications (email, Slack, etc.)    │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │                    │                                 │  │
│  │  ┌─────────────────▼────────────────────────────┐  │  │
│  │  │  Grafana                                      │  │  │
│  │  │  - Visualize metrics                          │  │  │
│  │  │  - Pre-configured dashboards                  │  │  │
│  │  │  - Alert visualization                        │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Components

### 1. Prometheus Operator

**Chart**: kube-prometheus-stack (version 80.7.0)
**Namespace**: monitoring
**Components**:
- Prometheus Operator
- Prometheus (v3.8.1)
- Alertmanager
- Grafana
- kube-state-metrics
- node-exporter

### 2. ServiceMonitors

Custom ServiceMonitors configured for scraping metrics:

- **todo-backend**: Scrapes metrics from backend API at `/metrics`
- **todo-notifications**: Scrapes metrics from notifications service at `/metrics`
- **dapr-sidecars**: Scrapes Dapr sidecar metrics
- **redpanda**: Scrapes Redpanda broker metrics

### 3. Prometheus Alerting Rules

Custom alerting rules configured in `alerting-rules.yaml`:

| Alert Name | Severity | Description |
|-----------|----------|-------------|
| PodCrashLooping | Warning | Pod is restarting frequently |
| HighCPUUsage | Warning | Container CPU usage > 80% |
| HighMemoryUsage | Warning | Container memory usage > 90% |
| ServiceDown | Critical | Service is not responding |
| DeploymentFailure | Warning | Deployment has unavailable replicas |
| PodNotReady | Warning | Pod is not ready |
| HighAPIErrorRate | Warning | API error rate > 5% |
| DatabaseConnectionFailure | Critical | No database connections |
| DaprSidecarNotReady | Warning | Dapr sidecar not responding |
| RedpandaBrokerDown | Critical | Redpanda broker is down |

### 4. Grafana Dashboards

Pre-configured dashboards:

1. **Kubernetes Cluster Health** (k8s-cluster-health-todo)
   - Total pods
   - Pods down
   - Crash looping pods
   - Cluster memory usage
   - CPU usage by pod
   - Memory usage by pod

2. **Backend Application Metrics** (Import from `grafana-dashboards/backend-application.json`)
   - Request rate
   - Error rate
   - P95 latency
   - Requests by endpoint
   - Request latency percentiles (P50, P95, P99)
   - Backend memory usage

## Installation

### Prerequisites

- Kubernetes cluster (DOKS or Minikube)
- kubectl configured
- Helm 3.x installed

### Deploy Monitoring Stack

The kube-prometheus-stack is already installed:

```bash
# Verify installation
helm list -n monitoring
kubectl get pods -n monitoring
```

### Deploy ServiceMonitors and Alerting Rules

```bash
# Apply ServiceMonitors
kubectl apply -f k8s/monitoring/servicemonitors.yaml

# Apply Prometheus alerting rules
kubectl apply -f k8s/monitoring/alerting-rules.yaml

# Apply Grafana dashboards
kubectl apply -f k8s/monitoring/dashboards-configmap-raw.yaml
```

### Verify Deployment

```bash
# Check ServiceMonitors
kubectl get servicemonitors -n production

# Check PrometheusRules
kubectl get prometheusrules -n production

# Check Prometheus targets
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Open http://localhost:9090/targets
```

## Access

### Grafana

**Credentials**:
- Username: `admin`
- Password: Get with: `kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode`

**Access Methods**:

1. **Port Forwarding** (Recommended for local):
```bash
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
# Open http://localhost:3000
```

2. **LoadBalancer** (For production):
```bash
kubectl patch svc prometheus-grafana -n monitoring -p '{"spec":{"type":"LoadBalancer"}}'
# Get external IP: kubectl get svc prometheus-grafana -n monitoring
```

### Prometheus

```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Open http://localhost:9090
```

### Alertmanager

```bash
kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093
# Open http://localhost:9093
```

## Application Metrics

### Backend Services

The backend services expose metrics at `/metrics` endpoint in Prometheus format. Services should instrument the following metrics:

```python
# Example using prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request latency histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Active connections gauge
active_connections = Gauge(
    'active_connections',
    'Number of active database connections'
)
```

### Dapr Metrics

Dapr sidecars expose metrics automatically. Metrics include:
- Service invocation counts
- Actor activations
- State operations
- Pub/sub message counts

### Redpanda Metrics

Redpanda exposes metrics at `/metrics`:
- Message rates
- Partition sizes
- Consumer lag
- Broker health

## Troubleshooting

### ServiceMonitors Not Working

1. Check ServiceMonitor labels match service labels:
```bash
kubectl get servicemonitors -n production -o yaml
kubectl get svc -n production --show-labels
```

2. Verify Prometheus is discovering targets:
```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Open http://localhost:9090/targets
```

### No Metrics from Backend Services

1. Check if `/metrics` endpoint is accessible:
```bash
kubectl exec -it <pod-name> -n production -- curl http://localhost:8000/metrics
```

2. Verify backend services have metrics configured:
```bash
kubectl logs <pod-name> -n production | grep -i prometheus
```

### Alerts Not Firing

1. Check PrometheusRules are loaded:
```bash
kubectl get prometheusrules -n production
```

2. Verify in Prometheus UI: http://localhost:9090/alerts

3. Check Alertmanager is receiving alerts:
```bash
kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093
# Open http://localhost:9093/#/alerts
```

## Configuration Files

| File | Description |
|------|-------------|
| `servicemonitors.yaml` | ServiceMonitors for backend services, Dapr, and Redpanda |
| `alerting-rules.yaml` | Prometheus alerting rules for the application |
| `dashboards-configmap-raw.yaml` | Grafana dashboard ConfigMap |
| `grafana-dashboards/k8s-cluster-health.json` | Kubernetes cluster health dashboard |
| `grafana-dashboards/backend-application.json` | Backend application metrics dashboard |
| `access-monitoring.sh` | Helper script to access monitoring services |

## Production Considerations

### Persistence

Prometheus and Grafana data should be persisted:

```bash
# Check PVCs
kubectl get pvc -n monitoring
```

### Scaling

For high-traffic scenarios:

1. Increase Prometheus retention:
```yaml
# In values.yaml
prometheus:
  prometheusSpec:
    retention: 30d
    retentionSize: 50GB
```

2. Enable Prometheus remote write for long-term storage

### Security

1. Enable Grafana anonymous viewing (read-only):
```yaml
grafana:
  grafana.ini:
    auth.anonymous:
      enabled: true
      org_name: Main Org.
      role: Viewer
```

2. Use TLS for all external access

3. Configure RBAC for Grafana

## Next Steps

1. **Configure Alert Notifications**: Set up email, Slack, or PagerDuty integration in Alertmanager
2. **Customize Dashboards**: Import additional dashboards from Grafana.com
3. **Set Up Recording Rules**: Create recording rules for complex queries
4. **Configure Remote Write**: Set up long-term metric storage
5. **Enable Tracing**: Integrate with Jaeger or OpenTelemetry for distributed tracing

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kube-Prometheus-Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Dapr Observability](https://docs.dapr.io/operations/observability/)

## Support

For issues or questions:
1. Check pod logs: `kubectl logs -n monitoring <pod-name>`
2. Check events: `kubectl describe pod -n monitoring <pod-name>`
3. Review Prometheus targets: http://localhost:9090/targets
4. Review Alertmanager status: http://localhost:9093/#/status
