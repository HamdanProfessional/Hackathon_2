#!/bin/bash
# Kafka Local Deployment Script for Minikube
# This script deploys Apache Kafka (Bitnami 3.5) which is compatible with Dapr

set -e

echo "========================================="
echo "Deploying Kafka for Local/Minikube Development"
echo "========================================="
echo ""

# Create namespace if it doesn't exist
echo "1. Creating kafka namespace..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Deploy Kafka and Zookeeper
echo ""
echo "2. Deploying Kafka and Zookeeper..."
kubectl apply -f k8s/kafka/kafka-local.yaml

# Wait for pods to be ready
echo ""
echo "3. Waiting for Kafka to be ready..."
echo "   (This may take 2-3 minutes)"
kubectl wait --for=condition=ready pod -l app=zookeeper -n kafka --timeout=300s || true
kubectl wait --for=condition=ready pod -l app=kafka -n kafka --timeout=300s || true

# Show status
echo ""
echo "4. Checking deployment status..."
kubectl get pods -n kafka
kubectl get svc -n kafka

# Deploy Dapr component
echo ""
echo "5. Deploying Dapr Kafka component..."
kubectl apply -f k8s/dapr-components/pubsub-kafka-local.yaml

echo ""
echo "========================================="
echo "Kafka deployment complete!"
echo "========================================="
echo ""
echo "Kafka broker: kafka.kafka.svc.cluster.local:9092"
echo ""
echo "Test Kafka connection:"
echo "  kubectl exec -n kafka deployment/kafka -- kafka-broker-api-versions --bootstrap-server localhost:9092"
echo ""
echo "View logs:"
echo "  kubectl logs -n kafka deployment/kafka -f"
echo ""
