# Kafka Deployment Quick Reference

## Current Status (2025-12-27)

### Working Configuration
- **Message Broker:** Dapr in-memory pub/sub
- **Namespace:** production
- **Component:** `todo-pubsub` (type: pubsub.in-memory)
- **Status:** Operational (development/testing only)
- **Services:** todo-notifications (2/2 pods running)

### Infrastructure Deployed
- **Redpanda Cluster:** Running in `redpanda-system` namespace
- **Kafka Namespace:** Created and ready for future Kafka deployment
- **Dapr:** Version 1.16.5 operational

## Redpanda Details

### Connection Information
```bash
# Internal cluster DNS
redpanda-0.redpanda.redpanda-system.svc.cluster.local:9093

# Service
kubectl get svc redpanda -n redpanda-system

# Topics
kubectl exec -n redpanda-system redpanda-0 -c redpanda -- rpk cluster info
```

### Available Topics
- task-created
- task-updated
- task-completed
- task-deleted
- task-due-soon
- recurring-task-due

### Management Commands
```bash
# List topics
kubectl exec -n redpanda-system redpanda-0 -c redpanda -- rpk topic list

# Describe topic
kubectl exec -n redpanda-system redpanda-0 -c redpanda -- rpk topic describe task-created

# Consume messages
kubectl exec -n redpanda-system redpanda-0 -c redpanda -- rpk topic consume task-created

# Produce message
kubectl exec -n redpanda-system redpanda-0 -c redpanda -- rpk topic produce task-created
```

## Dapr Pub/Sub Components

### Current: In-Memory (Development)
**File:** `k8s/dapr-components/pubsub-in-memory.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: production
spec:
  type: pubsub.in-memory
  version: v1
```

### Attempted: Kafka/Redpanda (Not Working)
**File:** `k8s/dapr-components/pubsub-kafka.yaml`
**Status:** Commented out - Dapr Kafka client incompatible with Redpanda v25.3.1

## Deployment Files

### Kafka Manifests (Created but Not Deployed)
```
k8s/kafka/
├── values.yaml                    # Bitnami Helm values
├── kafka-statefulset.yaml         # Kafka StatefulSet (KRaft mode)
├── single-kafka.yaml              # Single broker configuration
├── kafka-wurstmeister.yaml        # Wurstmeister image (failed)
├── bitnami-kafka-complete.yaml    # Bitnami Kafka + Zookeeper (failed)
└── deploy-kafka.sh                # Deployment script
```

### Dapr Components
```
k8s/dapr-components/
├── pubsub-in-memory.yaml          # Current: In-memory pubsub
├── pubsub-kafka.yaml              # Attempted: Kafka/Redpanda
├── pubsub-redpanda.yaml           # Original: Redpanda config
└── state-redis.yaml               # Redis state store
```

## Verification Commands

### Check Service Status
```bash
# Notification service
kubectl get pods -n production -l app=todo-notifications

# Dapr sidecar logs
kubectl logs -f todo-notifications-<pod-id> -n production -c daprd

# Check Dapr components
kubectl get components -n production
```

### Test Event Publishing
```bash
# Port forward to backend
kubectl port-forward -n production svc/todo-backend 8000:8000

# Publish event (via API or direct Dapr invoke)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing pubsub"}'
```

### Monitor Dapr Pub/Sub
```bash
# Check Dapr metrics
kubectl port-forward todo-notifications-<pod-id> -n production 9090:9090
curl http://localhost:9090/metrics | grep pubsub

# View Dapr logs
kubectl logs -f todo-notifications-<pod-id> -n production -c daprd | grep -i pubsub
```

## Next Steps for Production

### Option A: Deploy Apache Kafka with Zookeeper (Recommended)
1. Use Confluent Platform images (known to work with Dapr)
2. Deploy Zookeeper cluster (3 nodes)
3. Deploy Kafka cluster (3 nodes)
4. Configure external access via LoadBalancer
5. Update Dapr component to use new Kafka brokers
6. Test end-to-end event flow

### Option B: Upgrade Dapr (Alternative)
1. Check if newer Dapr version supports Redpanda v25.x
2. Test in development environment first
3. Upgrade Dapr sidecar injector
4. Rollout restart all services
5. Re-enable Kafka pubsub component

### Option C: Stay with In-Memory (Development Only)
- Accept limitations (no persistence, no cross-pod)
- Document clearly as development-only
- Plan migration to proper Kafka before production

## Troubleshooting

### Issue: Notification Pods CrashLoopBackOff
**Symptom:** Pods failing with Dapr initialization errors
**Solution:** Check Dapr component configuration, verify broker accessibility

### Issue: "EOF" Error Connecting to Redpanda
**Symptom:** Dapr logs show "client has run out of available brokers"
**Cause:** Dapr Sarama client incompatible with Redpanda v25.3.1
**Solution:** Use traditional Apache Kafka or upgrade Dapr

### Issue: Image Pull BackOff
**Symptom:** Kubernetes can't pull Kafka image
**Solution:** Verify image tag exists on Docker Hub, use alternative image

### Issue: Topics Not Auto-Created
**Symptom:** Dapr can't publish to topics
**Solution:** Create topics manually or enable auto-creation in broker config

## Performance Considerations

### In-Memory Pub/Sub (Current)
- **Throughput:** High (in-process)
- **Latency:** <1ms
- **Persistence:** None
- **Scalability:** Limited to single pod
- **Production Ready:** NO

### Apache Kafka (Recommended)
- **Throughput:** 100K+ msg/sec per cluster
- **Latency:** 2-5ms (same availability zone)
- **Persistence:** Configurable (days to weeks)
- **Scalability:** Horizontal scaling
- **Production Ready:** YES

### Redpanda (If Dapr Compatible)
- **Throughput:** Higher than Kafka (optimized C++)
- **Latency:** <2ms
- **Persistence:** Configurable
- **Scalability:** Horizontal scaling
- **Production Ready:** YES (if Dapr works)

## Monitoring

### Redpanda Console
```bash
# Port forward to Redpanda Console
kubectl port-forward -n redpanda-system svc/redpanda-console 8080:8080
# Access at http://localhost:8080
```

### Dapr Metrics
```bash
# Expose Dapr metrics endpoint
kubectl port-forward <pod-name> -n production 9090:9090
curl http://localhost:9090/metrics
```

### Kafka Monitoring (Future)
- JMX metrics → Prometheus
- Kafka UI or Burrow for consumer lag monitoring
- Alert on consumer group lag
- Monitor topic throughput and latency

## Documentation

- **Full Status:** `docs/KAFKA_DEPLOYMENT_STATUS.md`
- **Kubernetes Manifests:** `k8s/kafka/`
- **Dapr Components:** `k8s/dapr-components/`
- **Project Docs:** `docs/`

## Support

For issues or questions:
1. Check `docs/KAFKA_DEPLOYMENT_STATUS.md` for detailed analysis
2. Review deployment logs: `kubectl logs -n kafka`
3. Check Dapr logs: `kubectl logs -n production -c daprd`
4. Consult Dapr documentation: https://docs.dapr.io
