#!/bin/bash

# Monitoring Access Script for Todo App
# This script helps you access Grafana and Prometheus dashboards

set -e

NAMESPACE="monitoring"

echo "=================================="
echo "Todo App Monitoring Stack Access"
echo "=================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

# Get Grafana admin password
GRAFANA_PASSWORD=$(kubectl get secret prometheus-grafana -n $NAMESPACE -o jsonpath="{.data.admin-password}" | base64 --decode)

echo "GRAFANA CREDENTIALS:"
echo "-------------------"
echo "Username: admin"
echo "Password: $GRAFANA_PASSWORD"
echo ""

echo "ACCESS METHODS:"
echo "---------------"
echo ""
echo "Method 1: Port Forwarding (Recommended for local access)"
echo "---------------------------------------------------------"
echo ""
echo "To access Grafana:"
echo "  kubectl port-forward svc/prometheus-grafana -n $NAMESPACE 3000:80"
echo "  Then open: http://localhost:3000"
echo ""
echo "To access Prometheus:"
echo "  kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n $NAMESPACE 9090:9090"
echo "  Then open: http://localhost:9090"
echo ""
echo "To access Alertmanager:"
echo "  kubectl port-forward svc/prometheus-kube-prometheus-alertmanager -n $NAMESPACE 9093:9093"
echo "  Then open: http://localhost:9093"
echo ""
echo "Method 2: LoadBalancer (For remote access)"
echo "-------------------------------------------"
echo ""
echo "To expose Grafana via LoadBalancer:"
echo "  kubectl patch svc prometheus-grafana -n $NAMESPACE -p '{\"spec\":{\"type\":\"LoadBalancer\"}}'"
echo "  Then get external IP: kubectl get svc prometheus-grafana -n $NAMESPACE"
echo ""
echo "MONITORING ENDPOINTS:"
echo "---------------------"
echo ""
echo "ServiceMonitors configured:"
kubectl get servicemonitors -n production -o custom-columns="NAME:.metadata.name","AGE:.metadata.creationTimestamp" 2>/dev/null || echo "  No ServiceMonitors found"
echo ""
echo "PrometheusRules configured:"
kubectl get prometheusrules -n production -o custom-columns="NAME:.metadata.name","AGE:.metadata.creationTimestamp" 2>/dev/null || echo "  No PrometheusRules found"
echo ""
echo "DASHBOARD CONFIGURATION:"
echo "------------------------"
echo ""
echo "Grafana dashboards installed:"
echo "  - Kubernetes Cluster Health (k8s-cluster-health-todo)"
echo "  - Backend Application Metrics (to be imported manually)"
echo ""
echo "To import additional dashboards:"
echo "1. Log in to Grafana"
echo "2. Go to Dashboards -> Import"
echo "3. Upload dashboard JSON from k8s/monitoring/grafana-dashboards/"
echo ""
echo "=================================="
