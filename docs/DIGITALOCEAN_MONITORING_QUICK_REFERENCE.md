# Monitoring Quick Reference Guide

## Cluster Information

**Cluster Name**: do-fra1-hackathon2h1
**Region**: Frankfurt (fra1)
**Monitoring Namespace**: monitoring
**Production Namespace**: production

## Access Credentials

### Grafana
- **Username**: admin
- **Password**: admin
- **Access**: `kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80`
- **URL**: http://localhost:3000

### Prometheus
- **Access**: `kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090`
- **URL**: http://localhost:9090
- **Targets**: http://localhost:9090/targets
- **Alerts**: http://localhost:9090/alerts

### Alertmanager
- **Access**: `kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093`
- **URL**: http://localhost:9093
- **Alerts**: http://localhost:9093/#/alerts

## Deployed Resources

### ServiceMonitors (Production Namespace)
```bash
kubectl get servicemonitors -n production
```

Expected outputs:
- todo-backend
- todo-notifications
- dapr-sidecars
- redpanda

### PrometheusRules (Production Namespace)
```bash
kubectl get prometheusrules -n production
```

Expected outputs:
- todo-app-alerts

### Grafana Dashboards
1. Kubernetes Cluster Health - Todo App (k8s-cluster-health-todo)
2. Backend Application Metrics (import from JSON)

## Active Alerts

The following alerts are configured:

| Alert | Severity | Trigger | Duration |
|-------|----------|---------|----------|
| PodCrashLooping | Warning | Restart rate > 0 | 5m |
| HighCPUUsage | Warning | CPU > 80% | 10m |
| HighMemoryUsage | Warning | Memory > 90% | 5m |
| ServiceDown | Critical | Service unreachable | 5m |
| DeploymentFailure | Warning | Unavailable replicas > 0 | 10m |
| PodNotReady | Warning | Pod not ready | 10m |
| HighAPIErrorRate | Warning | Error rate > 5% | 5m |
| DatabaseConnectionFailure | Critical | No DB connections | 5m |
| DaprSidecarNotReady | Warning | Dapr not responding | 5m |
| RedpandaBrokerDown | Critical | Redpanda down | 5m |

## Common Commands

### Check Monitoring Stack Status
```bash
# All monitoring pods
kubectl get pods -n monitoring

# All ServiceMonitors
kubectl get servicemonitors -A

# All PrometheusRules
kubectl get prometheusrules -A

# Prometheus targets
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Then open: http://localhost:9090/targets
```

### View Logs
```bash
# Prometheus logs
kubectl logs -n monitoring prometheus-prometheus-kube-prometheus-prometheus-0 -c prometheus

# Grafana logs
kubectl logs -n monitoring prometheus-grafana-865fbb74d6-lzckg -c grafana

# Alertmanager logs
kubectl logs -n monitoring alertmanager-prometheus-kube-prometheus-alertmanager-0 -c alertmanager
```

### Access Dashboards
```bash
# Start Grafana port-forward
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80

# Start Prometheus port-forward
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090

# Start Alertmanager port-forward
kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093
```

### Troubleshooting
```bash
# Check ServiceMonitor configuration
kubectl describe servicemonitor <name> -n production

# Check PrometheusRule configuration
kubectl describe prometheusrule <name> -n production

# Check if Prometheus is discovering targets
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Open: http://localhost:9090/service-discovery

# View Prometheus configuration
kubectl exec -n monitoring prometheus-prometheus-kube-prometheus-prometheus-0 -- cat /etc/prometheus/config_out/prometheus.env.yaml
```

## Metrics Collection

### Backend Services

Todo backend services expose metrics at `/metrics`:

```bash
# Test metrics endpoint
kubectl exec -it <pod-name> -n production -- curl http://localhost:8000/metrics
```

### Dapr Metrics

Dapr sidecars expose metrics automatically:

```bash
# Get Dapr metrics
kubectl exec -it <pod-name> -n production -c daprd -- curl http://localhost:9090/metrics
```

### Redpanda Metrics

Redpanda exposes metrics:

```bash
# Get Redpanda pods
kubectl get pods -n redpanda-system

# Get metrics from a pod
kubectl exec -it <redpanda-pod> -n redpanda-system -- curl http://localhost:9644/metrics
```

## Performance Tuning

### Prometheus Storage
```bash
# Check PVC usage
kubectl get pvc -n monitoring

# Check Prometheus storage usage
kubectl exec -n monitoring prometheus-prometheus-kube-prometheus-prometheus-0 -- df -h /prometheus
```

### Reduce Retention (if needed)
Edit the Helm values:
```yaml
prometheus:
  prometheusSpec:
    retention: 15d  # Default is usually longer
    retentionSize: 10GB
```

### Increase Scrape Interval
If you need less frequent scraping:
```yaml
prometheus:
  prometheusSpec:
    scrapeInterval: 60s  # Default is 30s
```

## Alert Notifications

To configure alert notifications (email, Slack, etc.):

1. Edit Alertmanager ConfigMap:
```bash
kubectl edit configmap alertmanager-prometheus-kube-prometheus-alertmanager -n monitoring
```

2. Or use Helm values to configure alertmanager.yaml

## Dashboard Links

Once you access Grafana, look for:

1. **Kubernetes Cluster Health**:
   - Overview of all pods in production namespace
   - CPU and memory usage by pod
   - Cluster health indicators

2. **Import Backend Dashboard**:
   - Go to Dashboards -> Import
   - Upload `k8s/monitoring/grafana-dashboards/backend-application.json`
   - Select Prometheus as datasource

## Emergency Procedures

### Restart Monitoring Stack
```bash
# Restart Prometheus
kubectl delete pod prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring

# Restart Grafana
kubectl delete pod -l app.kubernetes.io/name=grafana -n monitoring

# Restart Alertmanager
kubectl delete pod alertmanager-prometheus-kube-prometheus-alertmanager-0 -n monitoring
```

### Clear Alerts
```bash
# Access Alertmanager UI
kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n monitoring 9093:9093
# Open: http://localhost:9093/#/alerts
```

### Scale Resources
```bash
# Edit Prometheus resources
kubectl edit prometheus prometheus-kube-prometheus-prometheus -n monitoring

# Edit Grafana resources
kubectl edit deployment prometheus-grafana -n monitoring
```

## Next Steps

1. Configure external access (LoadBalancer or Ingress)
2. Set up alert notification channels
3. Import additional Grafana dashboards
4. Configure persistent storage backup
5. Set up log aggregation (Loki, ELK)
6. Enable distributed tracing (Jaeger, Tempo)

## Support

For detailed documentation, see: `k8s/monitoring/README.md`

For quick access script, run:
```bash
bash k8s/monitoring/access-monitoring.sh
```
