# Apache Kafka Deployment Status - DigitalOcean Kubernetes

**Date:** 2025-12-27
**Cluster:** do-fra1-hackathon2h1 (Frankfurt)
**Namespace:** kafka

## Executive Summary

After multiple attempts to deploy Apache Kafka on DigitalOcean Kubernetes Service (DOKS), we encountered persistent issues with Docker image availability and compatibility. The current status is:

- **Current Solution:** Using Dapr in-memory pub/sub (temporary workaround)
- **Redpanda Status:** Deployed and working, but incompatible with Dapr Kafka component
- **Kafka Deployment:** Multiple attempts failed due to image pull issues

## Deployment Attempts

### Attempt 1: Bitnami Kafka Helm Chart
**Chart:** `oci://registry-1.docker.io/bitnamicharts/kafka`
**Version:** 32.4.3 (Kafka 4.0.0)
**Status:** Failed

**Issue:**
```
Failed to pull image "docker.io/bitnami/kafka:4.0.0-debian-12-r10": not found
```

**Attempted Solutions:**
- Tried different image tags (3.7.1, 3.6, latest)
- All resulted in "ImagePullBackOff" or tag not found errors

### Attempt 2: Confluent Kafka with KRaft Mode
**Image:** `confluentinc/cp-kafka:7.7.1`
**Status:** Failed

**Issue:**
```
Error: failed to create containerd task: read-only file system
```

**Configuration:**
- KRaft mode (no ZooKeeper)
- Custom server.properties via ConfigMap
- Proper CLUSTER_ID generation

### Attempt 3: Wurstmeister Kafka + Zookeeper
**Image:** `wurstmeister/kafka:2.13-2.8.1`
**Status:** Failed

**Issue:**
```
Missing privilege separation directory: /var/run/sshd
```

### Attempt 4: Bitnami Kafka + Zookeeper (Separate)
**Images:**
- `bitnami/kafka:3.5`
- `bitnami/zookeeper:3.8.1`

**Status:** Failed

**Issue:** Image tags not available on Docker Hub

## Current Infrastructure

### Redpanda Cluster (Working)
- **Version:** v25.3.1
- **Namespace:** `redpanda-system`
- **Pods:** 1 controller (redpanda-0)
- **Status:** Running successfully
- **Topics:** All Todo app topics created (6 topics)
- **Port:** 9093 (Kafka API)

**Connection String:**
```
redpanda-0.redpanda.redpanda-system.svc.cluster.local:9093
```

**Topics:**
- task-created
- task-updated
- task-completed
- task-deleted
- task-due-soon
- recurring-task-due

### Dapr Configuration
**Current Component:** `pubsub.in-memory`
**Namespace:** `production`
**Status:** Working (temporary solution)

**Kafka Component Attempt:**
```
Error: kafka: client has run out of available brokers to talk to: EOF
```

This suggests a protocol incompatibility between Dapr's Kafka client (based on Sarama) and Redpanda v25.3.1.

## Root Cause Analysis

### 1. Image Availability Issues
Bitnami images have complex versioning on Docker Hub. The tag format often doesn't match what Helm charts expect, leading to pull failures.

### 2. Redpanda Incompatibility
Dapr uses the Sarama Go Kafka client library, which has known compatibility issues with Redpanda v25.3.1. The error "EOF" when connecting suggests:
- Protocol version mismatch
- TLS handshake failure (even with TLS disabled)
- Broker metadata exchange failure

### 3. KRaft Mode Complexity
Modern Kafka (3.x+) uses KRaft mode instead of ZooKeeper, but:
- Configuration is more complex
- Many Helm charts and images don't support it properly
- Requires precise cluster ID and controller quorum setup

## Recommended Solutions

### Option 1: Use Apache Kafka with Zookeeper (RECOMMENDED)
Deploy a traditional Kafka 2.x or 3.x with ZooKeeper using proven images:

```yaml
# Use Confluent Platform images (reliable)
repository: confluentinc/cp-kafka
tag: 7.4.0  # Known good version

# Use Confluent Zookeeper
repository: confluentinc/cp-zookeeper
tag: 7.4.0
```

**Advantages:**
- Proven compatibility with Dapr
- Well-documented
- Stable and production-ready

**Implementation:**
1. Deploy Zookeeper first (3 replicas for HA)
2. Deploy Kafka with proper advertised listeners
3. Use external access via LoadBalancer
4. Configure Dapr with broker address

### Option 2: Upgrade Dapr to Support Redpanda
Check for Dapr version that supports newer Kafka protocol versions:

```bash
# Current Dapr version: 1.16.5
# Check for updates
kubectl get deployment dapr-sidecar-injector -n dapr-system -o yaml | grep image
```

**Advantages:**
- No new infrastructure needed
- Redpanda already working

**Disadvantages:**
- May require Dapr upgrade
- Risk of breaking other Dapr components

### Option 3: Use Kafka Bridge
Deploy a Kafka protocol-compatible bridge:

```yaml
# Use MirrorMaker or Kafka Connect
# to bridge between Redpanda and Dapr
```

**Advantages:**
- Keeps Redpanda
- Adds compatibility layer

**Disadvantages:**
- Additional infrastructure
- More moving parts

### Option 4: Stay with In-Memory Pub/Sub (CURRENT)
For development and testing only:

**Advantages:**
- No infrastructure needed
- Works immediately

**Disadvantages:**
- Not production-ready
- No message persistence
- No cross-pod communication

## Action Items for Production

### Immediate (Required for Production)
1. [ ] Deploy Apache Kafka 2.8.x or 3.4.x with ZooKeeper
2. [ ] Configure 3-node Kafka cluster for high availability
3. [ ] Set up JMX monitoring with Prometheus
4. [ ] Configure Dapr Kafka pubsub component
5. [ ] Test end-to-end event flow
6. [ ] Implement topic retention policies

### Short-term (Recommended)
1. [ ] Set up Kafka Manager or UI for monitoring
2. [ ] Configure alerting for consumer lag
3. [ ] Implement dead letter queues
4. [ ] Add Kafka topic auto-creation policies
5. [ ] Document disaster recovery procedures

### Long-term (Optimization)
1. [ ] Consider migrating to KRaft mode once stabilized
2. [ ] Implement schema registry (Confluent Schema Registry)
3. [ ] Add Kafka Connect for data integration
4. [ ] Set up Kafka multi-region replication

## Files Created

### Kubernetes Manifests
- `k8s/kafka/values.yaml` - Bitnami Kafka Helm values
- `k8s/kafka/kafka-statefulset.yaml` - Kafka StatefulSet manifest
- `k8s/kafka/single-kafka.yaml` - Single Kafka broker configuration
- `k8s/kafka/kafka-wurstmeister.yaml` - Wurstmeister Kafka deployment
- `k8s/kafka/bitnami-kafka-complete.yaml` - Bitnami Kafka + Zookeeper
- `k8s/kafka/deploy-kafka.sh` - Kafka deployment script

### Dapr Components
- `k8s/dapr-components/pubsub-kafka.yaml` - Dapr Kafka pubsub (commented out, not working)
- `k8s/dapr-components/pubsub-in-memory.yaml` - Current working solution

## Lessons Learned

1. **Image Tag Verification:** Always verify Docker Hub image tags before using them in Helm charts or manifests
2. **Version Compatibility:** Dapr's Kafka client (Sarama) may not support the latest Kafka protocol versions
3. **KRaft vs ZooKeeper:** KRaft is the future but ZooKeeper-based setups are more stable currently
4. **Redpanda vs Kafka:** Redpanda is Kafka-compatible but not 100% protocol-identical
5. **Start Simple:** Begin with single-node deployments before scaling to multi-node clusters

## Next Steps

1. **Immediate:** Stay with in-memory pub/sub for development
2. **This Week:** Deploy proven Kafka 2.8/3.4 with ZooKeeper
3. **Next Sprint:** Migrate to production Kafka cluster
4. **Future:** Evaluate KRaft mode or Redpanda upgrade

## References

- [Dapr Kafka PubSub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-kafka/)
- [Bitnami Kafka Helm Chart](https://github.com/bitnami/charts/tree/main/bitnami/kafka)
- [Confluent Platform Docker Images](https://hub.docker.com/r/confluentinc/cp-kafka)
- [Redpanda v25 Compatibility](https://docs.redpanda.com/current/release-notes/25/)
- [Apache Kafka KRaft Mode](https://kafka.apache.org/documentation/#kraft)

## Contact

For questions or issues with this deployment, refer to:
- Infrastructure documentation: `docs/`
- Kubernetes manifests: `k8s/`
- Dapr components: `k8s/dapr-components/`
