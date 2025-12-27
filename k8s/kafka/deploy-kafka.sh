#!/bin/bash
# Deploy Apache Kafka 3.7 on Kubernetes (KRaft mode, no ZooKeeper)

set -e

NAMESPACE="kafka"
CLUSTER_ID="5VXo2vFlQae6JRGmA9q8Lg"

echo "Deploying Kafka cluster to namespace: $NAMESPACE"

# Create ConfigMap with Kafka configuration
kubectl create configmap kafka-config \
  --from-literal=KAFKA_CLUSTER_ID=$CLUSTER_ID \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy Kafka brokers
for i in 0 1 2; do
  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kafka-data-$i
  namespace: $NAMESPACE
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: do-block-storage
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-$i
  namespace: $NAMESPACE
  labels:
    app: kafka
    broker-id: "$i"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka
      broker-id: "$i"
  template:
    metadata:
      labels:
        app: kafka
        broker-id: "$i"
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:7.7.1
        ports:
        - containerPort: 9092
          name: plaintext
        - containerPort: 9093
          name: controller
        env:
        - name: KAFKA_NODE_ID
          value: "$i"
        - name: KAFKA_CLUSTER_ID
          value: "$CLUSTER_ID"
        - name: KAFKA_PROCESS_ROLES
          value: "broker,controller"
        - name: KAFKA_CONTROLLER_QUORUM_VOTERS
          value: "0@kafka-0.kafka-headless.$NAMESPACE.svc.cluster.local:9093,1@kafka-1.kafka-headless.$NAMESPACE.svc.cluster.local:9093,2@kafka-2.kafka-headless.$NAMESPACE.svc.cluster.local:9093"
        - name: KAFKA_LISTENERS
          value: "PLAINTEXT://:9092,CONTROLLER://:9093"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "PLAINTEXT://kafka-$i.kafka-headless.$NAMESPACE.svc.cluster.local:9092"
        - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
          value: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
        - name: KAFKA_CONTROLLER_LISTENER_NAMES
          value: "CONTROLLER"
        - name: KAFKA_INTER_BROKER_LISTENER_NAME
          value: "PLAINTEXT"
        - name: KAFKA_LOG_DIRS
          value: /var/lib/kafka/data
        - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
          value: "true"
        - name: KAFKA_NUM_PARTITIONS
          value: "3"
        - name: KAFKA_DEFAULT_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_MIN_INSYNC_REPLICAS
          value: "2"
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "3"
        volumeMounts:
        - name: data
          mountPath: /var/lib/kafka/data
        resources:
          requests:
            cpu: 500m
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: kafka-data-$i
EOF
done

echo "Waiting for Kafka brokers to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka -n $NAMESPACE --timeout=300s

echo "Kafka cluster deployed successfully!"
