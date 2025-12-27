# Monitoring Stack Installation Summary

## Installation Date
**December 26, 2025**

## Cluster Details
- **Cluster**: do-fra1-hackathon2h1 (DigitalOcean Kubernetes - Frankfurt)
- **Monitoring Namespace**: monitoring
- **Production Namespace**: production
- **Helm Chart**: kube-prometheus-stack v80.7.0

## Installed Components

### 1. Prometheus Operator Stack
Status: Already Installed and Running

| Component | Status | Replicas | Age |
|-----------|--------|----------|-----|
| Prometheus Operator | Running | 1/1 | 104m |
| Prometheus | Running | 2/2 | 104m |
| Alertmanager | Running | 2/2 | 104m |
| Grafana | Running | 3/3 | 104m |
| kube-state-metrics | Running | 1/1 | 104m |
| node-exporter | Running | 1/1 | 104m |

### 2. ServiceMonitors
Status: Created and Active

| ServiceMonitor | Namespace | Target | Port | Path | Interval |
|----------------|-----------|--------|------|------|----------|
| todo-backend | production | todo-backend | http | /metrics | 30s |
| todo-notifications | production | todo-notifications | http | /metrics | 30s |
| dapr-sidecars | production | Dapr sidecars | metrics | / | 30s |
| redpanda | redpanda-system | Redpanda broker | prometheus | /metrics | 30s |

### 3. Prometheus Alerting Rules
Status: Created and Active

**Rule Group**: todo-app-alerts (10 rules defined)

| Alert Name | Severity | Duration | Description |
|------------|----------|----------|-------------|
| PodCrashLooping | Warning | 5m | Pod is restarting frequently |
| HighCPUUsage | Warning | 10m | Container CPU usage > 80% |
| HighMemoryUsage | Warning | 5m | Container memory usage > 90% |
| ServiceDown | Critical | 5m | Service is not responding |
| DeploymentFailure | Warning | 10m | Deployment has unavailable replicas |
| PodNotReady | Warning | 10m | Pod is not ready |
| HighAPIErrorRate | Warning | 5m | API error rate > 5% |
| DatabaseConnectionFailure | Critical | 5m | No database connections |
| DaprSidecarNotReady | Warning | 5m | Dapr sidecar not responding |
| RedpandaBrokerDown | Critical | 5m | Redpanda broker is down |

### 4. Grafana Dashboards
Status: Configured

1. **Kubernetes Cluster Health - Todo App**
   - UID: k8s-cluster-health-todo
   - Panels: 6
   - Auto-provisioned via ConfigMap

2. **Backend Application Metrics**
   - Available as JSON for manual import
   - Location: k8s/monitoring/grafana-dashboards/backend-application.json
   - Panels: 7

## Access Information

### Grafana
- **Username**: admin
- **Password**: admin
- **Port Forward Command**:
  ```bash
  kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
  ```
- **URL**: http://localhost:3000
- **ConfigMaps**: todo-app-dashboards, prometheus-grafana-config-dashboards

### Prometheus
- **Port Forward Command**:
  ```bash
  kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
  ```
- **URL**: http://localhost:9090
- **Targets Page**: http://localhost:9090/targets
- **Alerts Page**: http://localhost:9090/alerts

### Alertmanager
- **Port Forward Command**:
  ```bash
  kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093
  ```
- **URL**: http://localhost:9093
- **Alerts Page**: http://localhost:9093/#/alerts

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| ServiceMonitors | k8s/monitoring/servicemonitors.yaml | Define metrics scraping targets |
| Alerting Rules | k8s/monitoring/alerting-rules.yaml | Define Prometheus alerting rules |
| Dashboard ConfigMap | k8s/monitoring/dashboards-configmap-raw.yaml | Load dashboards into Grafana |
| K8s Cluster Dashboard | k8s/monitoring/grafana-dashboards/k8s-cluster-health.json | Cluster health dashboard |
| Backend Dashboard | k8s/monitoring/grafana-dashboards/backend-application.json | Backend metrics dashboard |
| Access Script | k8s/monitoring/access-monitoring.sh | Quick access helper script |

## Verification Steps

### 1. Check Monitoring Stack Health
```bash
kubectl get pods -n monitoring
```

Expected: All pods Running (2/2 or 3/3 for some)

### 2. Check ServiceMonitors
```bash
kubectl get servicemonitors -n production
```

Expected: 4 ServiceMonitors (todo-backend, todo-notifications, dapr-sidecars, redpanda)

### 3. Check PrometheusRules
```bash
kubectl get prometheusrules -n production
```

Expected: 1 PrometheusRule (todo-app-alerts)

### 4. Verify Prometheus Targets
```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Open http://localhost:9090/targets
```

Expected: todo-backend and todo-notifications should appear as targets (once /metrics endpoint is available)

### 5. Check Grafana Dashboards
```bash
kubectl get configmap -n monitoring | grep dashboard
```

Expected: todo-app-dashboards, prometheus-grafana-config-dashboards

## Important Notes

### Metrics Endpoint Requirements
The backend services (todo-backend and todo-notifications) need to expose metrics at `/metrics` endpoint in Prometheus format. This requires:

1. **Backend Code Integration**:
   ```python
   from prometheus_client import Counter, Histogram, start_http_server

   # Define metrics
   http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
   http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency')

   # Expose metrics endpoint
   start_http_server(8000)
   ```

2. **FastAPI Integration**:
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator

   app = FastAPI()
   Instrumentator().instrument(app).expose(app)
   ```

### Current Limitations
- Backend services do not currently have Prometheus instrumentation
- ServiceMonitors are configured but will show no metrics until /metrics endpoint is implemented
- Alerts are configured but will only fire once metrics are available

### Next Steps
1. Add Prometheus instrumentation to backend services
2. Verify metrics are being scraped in Prometheus UI
3. Import backend application dashboard into Grafana
4. Configure alert notification channels (email, Slack, etc.)
5. Set up persistent storage backup
6. Consider enabling distributed tracing

## Documentation

- **Full Documentation**: k8s/monitoring/README.md
- **Quick Reference**: docs/DIGITALOCEAN_MONITORING_QUICK_REFERENCE.md
- **Access Helper**: k8s/monitoring/access-monitoring.sh

## Support

For issues:
1. Check pod logs: `kubectl logs -n monitoring <pod-name>`
2. Check events: `kubectl describe pod -n monitoring <pod-name>`
3. Verify targets: http://localhost:9090/targets
4. Review alerting rules: http://localhost:9090/alerts

## Status Summary

**Overall Status**: Monitoring Stack Installed and Configured

- Prometheus Operator: Running
- Grafana: Running with dashboards loaded
- Alertmanager: Running with alert rules configured
- ServiceMonitors: Created and active
- Next Action: Add Prometheus instrumentation to backend services

---

**Generated**: 2025-12-26
**Cluster**: do-fra1-hackathon2h1 (DigitalOcean)
**Region**: Frankfurt (fra1)
