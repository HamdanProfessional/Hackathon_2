# Research & Technology Decisions: Cloud Deployment with Event-Driven Architecture

**Date**: 2025-12-23
**Phase**: V - Cloud Deployment
**Purpose**: Resolve technical unknowns for event-driven architecture, Dapr integration, and cloud deployment

---

## 1. Dapr Integration Pattern

### Decision: Sidecar Pattern with Pub/Sub over Direct Service Communication

**Chosen Approach**: Each microservice has Dapr sidecar injected, all service-to-service communication goes through Dapr pub/sub, no direct HTTP calls between services.

**Implementation Pattern**:
```python
# Publisher (Backend)
from dapr import DaprClient

class TaskCreatedPublisher:
    def __init__(self):
        self.dapr = DaprClient()

    async def publish(self, task: Task):
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task-created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
        }
        self.dapr.publish_event(
            pubsub_name="todo-pubsub",
            topic_name="task-created",
            data=json.dumps(event),
            data_content_type="application/json"
        )

# Subscriber (Notification Service)
from dapr.ext.fastapi import DaprApp

dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def handle_task_created(event_data: dict):
    await process_task_event(event_data)
```

**Rationale**:
- Loose coupling: services don't need to know each other's endpoints
- At-least-once delivery: Dapr handles retries and acknowledgments
- Horizontal scaling: any service instance can consume events
- Observability: all events flow through Dapr for monitoring

**Alternatives Considered**:
- **Direct HTTP calls**: Rejected due to tight coupling and retry complexity
- **Shared message queue service**: Rejected as unnecessary abstraction layer
- **gRPC streaming**: Rejected due to complexity and Dapr's HTTP-first approach

**Event Ordering**:
- Dapr uses Kafka partitions for ordering within keys
- Events for same user go to same partition (partition by user_id)
- Global ordering not required (compensating actions instead)

**Dead Letter Queue**:
- Failed events after max retries go to DLQ topic
- Separate worker processes DLQ for manual intervention
- Alerts on DLQ accumulation

---

## 2. Redpanda vs Managed Kafka

### Decision: Self-Managed Redpanda on Kubernetes

**Chosen Approach**: Deploy Redpanda (Kafka-compatible) on Kubernetes cluster rather than using managed Kafka services.

**Implementation**:
```bash
# Install Redpanda via Helm
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda \
  --set replicas=3 \
  --set persistence.size=100Gi \
  --set resources.limits.cpu=4 \
  --set resources.limits.memory=8Gi
```

**Rationale**:
- **Cost effective**: No per-partition pricing like Confluent Cloud
- **Control**: Full control over configuration and tuning
- **Performance**: Redpanda advertises 10x lower latency than Kafka
- **Compatibility**: Drop-in replacement for Kafka clients
- **Self-contained**: Runs on same cluster as applications

**Alternatives Considered**:
- **Confluent Cloud**: Rejected due to high cost ($1000+/month for production)
- **AWS MSK**: Rejected due to vendor lock-in
- **Google Pub/Sub**: Rejected due to different API and learning curve
- **Azure Event Hubs**: Rejected due to different API and learning curve

**Redpanda Configuration**:
- 3 brokers (minimum for production HA)
- Replication factor: 3
- Partition count: 3 per topic
- Retention: 7 days (task events), 1 day (due notifications)
- Compression: snappy for balance of CPU vs size

**Resource Sizing**:
- Per broker: 4 CPU, 8Gi RAM
- Storage: 100Gi per broker (300Gi total)
- Network: LoadBalancer service for external access (development)

---

## 3. Notification Service Architecture

### Decision: Background Worker + Scheduled Jobs Pattern

**Chosen Approach**: Notification service runs FastAPI with background tasks plus scheduled cron jobs for periodic checks.

**Implementation Pattern**:
```python
# services/notifications/app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(
        check_due_tasks,
        "interval",
        hours=1,
        id="due-check-hourly"
    )
    scheduler.add_job(
        process_recurring_tasks,
        "cron",
        hour=2,  # Run at 2 AM daily
        id="recurring-daily"
    )
    scheduler.start()

@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.shutdown()

async def check_due_tasks():
    """Find tasks due within 24 hours and schedule notifications"""
    async with get_db() as db:
        tasks = await get_tasks_due_soon(db, hours=24)
        for task in tasks:
            if not task.notified:
                await send_notification(task)
                task.notified = True
                await db.commit()
```

**Rationale**:
- **Simplicity**: No external job scheduler needed (Celery, etc.)
- **Integrated**: Scheduler runs in same process as API
- **Reliability**: Kubernetes restarts recreate scheduler automatically
- **Visibility**: API endpoint `/workers/status` shows job status

**Alternatives Considered**:
- **Celery + Redis**: Rejected as additional infrastructure components
- **Kubernetes CronJob**: Rejected due to complexity (need separate Job/CRD per job)
- **Cloud Functions (GCF/Lambda)**: Rejected due to cold starts and complexity
- **External cron (GitHub Actions)**: Rejected due to slow execution interval

**Scaling Notification Service**:
- Horizontal Pod Autoscaler based on CPU/memory
- Multiple instances process different recurring tasks
- Dapr pub/sub ensures each task processed once (consumer groups)

---

## 4. CI/CD Pipeline Design

### Decision: GitHub Actions with Self-Hosted Runner Pattern

**Chosen Approach**: GitHub Actions workflow with optional self-hosted runners for production deployments.

**Implementation Pattern**:
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run tests
      run: |
        cd backend && pip install -r requirements.txt && pytest
        cd frontend && npm test

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
    - uses: actions/checkout@v4
    - name: Build and push images
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}-frontend:${{ github.sha }}
          ghcr.io/${{ github.repository }}-backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-production:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      KUBECONFIG: ${{ secrets.KUBECONFIG_PROD }}
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        helm upgrade --install todo-app ./helm/todo-app \
          --set image.tag=${{ github.sha }} \
          --namespace production
```

**Rationale**:
- **Native GitHub integration**: No external CI/CD platform needed
- **Free for public repos**: No additional cost
- **Matrix builds**: Can test across multiple Python/Node versions
- **Secrets management**: GitHub Secrets for sensitive data
- **Self-hosted option**: Can run runners on own infrastructure for cost/privacy

**Alternatives Considered**:
- **CircleCI**: Rejected due to additional cost and account management
- **GitLab CI**: Rejected as project uses GitHub
- **Jenkins**: Rejected due to maintenance overhead
- **ArgoCD**: Rejected as GitOps pattern overkill for this phase

**Deployment Strategy**:
- Blue-green deployments for zero downtime
- Helm rollback on failure
- Health check after deployment
- Automatic rollback on health check failure

---

## 5. Cloud Platform Selection

### Decision: DigitalOcean Kubernetes (DOKS) for Production Deployment

**Chosen Approach**: Deploy to DigitalOcean Kubernetes Service (DOKS) as the primary cloud platform for production.

**Implementation**:
```bash
# Install doctl
brew install doctl  # macOS
# Or download from https://github.com/digitalocean/doctl/releases

# Authenticate
doctl auth init

# Create DOKS cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify cluster
kubectl get nodes
```

**DigitalOcean Services Used**:

| Service | Purpose | Monthly Cost |
|---------|---------|--------------|
| **DOKS Cluster** | Kubernetes control plane + 3 nodes (s-4vcpu-8gb) | $60/mo |
| **Load Balancers** | 3 × DO Load Balancer (frontend, backend, notifications) | $36/mo |
| **Managed Redis** | Dapr state store (1GB Basic tier) | $15/mo |
| **Block Storage** | 3× 50GB volumes for Redpanda persistence | $12/mo |
| **Container Registry** | Docker image storage (~5GB) | ~$5/mo |
| **Cloud Firewalls** | Network security (included) | Free |
| **Bandwidth** | Included with Load Balancers | Free |
| **Total** | | **~$128/mo** |

**Why DigitalOcean?**

1. **Simplicity & Developer Experience**
   - Clean, intuitive web UI
   - Straightforward pricing without hidden fees
   - Excellent documentation and community
   - No complex IAM/IAM permissions like AWS/GCP

2. **Cost-Effectiveness**
   - DOKS is significantly cheaper than GKE/AKS
   - No control plane fees (unlike EKS/GKE)
   - Load Balancers only $12/mo vs $20+ on other clouds
   - Bandwidth included with Load Balancers

3. **All-in-One Platform**
   - Managed databases (PostgreSQL, Redis, MySQL)
   - Container Registry with CI/CD integration
   - Object Storage (Spaces) for static assets
   - Cloud Firewalls for security

4. **Performance**
   - Fast SSD storage on all nodes
   - 10 Gbps networking between nodes
   - Global data centers (NYC, SFO, AMS, FRA, SGP, BLR)
   - 99.95% uptime SLA

5. **doctl CLI**
   - First-class CLI tool for all operations
   - Can script entire infrastructure setup
   - Integrates with kubectl seamlessly

**DigitalOcean vs Alternatives**:

| Feature | DigitalOcean (DOKS) | Google Cloud (GKE) | Azure (AKS) |
|---------|-------------------|-------------------|-------------|
| **Monthly Cost** | ~$128/mo | ~$180+/mo | ~$150+/mo |
| **Control Plane** | Free | $74/mo | $0 (in-cluster) |
| **Load Balancer** | $12/mo each | $18/mo each | $18/mo each |
| **Block Storage** | $0.10/GB | $0.04/GB | $0.05/GB |
| **Managed Redis** | $15/mo (1GB) | ~$25/mo | ~$20/mo |
| **Container Registry** | ~$5/mo (5GB) | Free tier, then ~$7/mo | ~$5/mo |
| **Free Credits** | None for new users | $300 for 90 days | $200 for 30 days |
| **SLA** | 99.95% | 99.5% (monthly) | 99.95% |
| **Management UI** | Simple, clean | Complex (GCP Console) | Complex (Azure Portal) |
| **Learning Curve** | Low | High | High |

**DigitalOcean Regions**:

| Region | Location | Latency to US East |
|--------|----------|-------------------|
| NYC1 | New York, USA | Best (east coast) |
| NYC2 | New York, USA | Best (east coast) |
| NYC3 | New York, USA | Best (east coast) |
| SFO1 | San Francisco, USA | Good (west coast) |
| SFO2 | San Francisco, USA | Good (west coast) |
| SFO3 | San Francisco, USA | Good (west coast) |
| AMS2 | Amsterdam, NL | Good (Europe) |
| AMS3 | Amsterdam, NL | Good (Europe) |
| FRA1 | Frankfurt, DE | Good (Europe) |
| LON1 | London, UK | Good (Europe) |

**Recommendation**: Use **NYC1** or **NYC3** for lowest latency to US East users (likely hackathon judges location). **AMS3** or **FRA1** if targeting European users.

**Cost Optimization**:

1. **Use autoscaling** to scale down to 2 nodes during low traffic
2. **Shared Load Balancer** - Consider using single LB with Ingress Controller (nginx) to save $24/mo
3. **Preemptible nodes** - Not available on DO, but can use basic droplets instead of premium
4. **Free tier alternatives** - For testing, use Minikube locally instead of DO resources

**Migration Path**:
- If needed, can migrate from DOKS to GKE/AKS by exporting manifests
- Kubernetes manifests are portable across clouds
- Only Load Balancer and Storage configs need changes

---

## 6. Monitoring Strategy

### Decision: kube-prometheus-stack for All-in-One Monitoring

**Chosen Approach**: Deploy Prometheus, Grafana, AlertManager, Node Exporter as single Helm chart.

**Implementation**:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123
```

**Monitoring Targets**:

1. **Cluster Metrics** (Node Exporter)
   - CPU, memory, disk, network
   - Per-node and per-pod breakdown

2. **Application Metrics** (ServiceMonitors)
   - HTTP request rate, latency, errors
   - Task creation/completion rates
   - Dapr sidecar metrics

3. **Business Metrics** (Custom)
   - Tasks created per day
   - Recurring tasks active
   - Notifications sent

**Rationale**:
- **Comprehensive**: Single chart covers all monitoring needs
- **Grafana integration**: Pre-built dashboards included
- **AlertManager**: Native alert routing (email, Slack, PagerDuty)
- **Scalable**: Handles 1000+ pods easily

**Dashboards**:
- Kubernetes Cluster Overview
- Kubernetes Pod Monitoring
- Node Exporter Full
- Dapr Metrics (custom)
- Todo Application Metrics (custom)

---

## 7. Recurring Task Calculation Logic

### Decision: Database Query + Worker Processing

**Chosen Approach**: Store next_due_at in database, worker queries for due tasks and creates occurrences.

**Implementation**:
```python
def calculate_next_due_at(recurring_task: RecurringTask) -> datetime:
    """Calculate next occurrence based on recurrence pattern"""
    if not recurring_task.last_created_at:
        return recurring_task.start_date

    last = recurring_task.last_created_at

    if recurring_task.recurrence_type == "daily":
        return last + timedelta(days=recurring_task.recurrence_interval)

    elif recurring_task.recurrence_type == "weekly":
        return last + timedelta(weeks=recurring_task.recurrence_interval)

    elif recurring_task.recurrence_type == "monthly":
        # Approximate month (30 days)
        return last + timedelta(days=30 * recurring_task.recurrence_interval)

    elif recurring_task.recurrence_type == "yearly":
        # Approximate year (365 days)
        return last + timedelta(days=365 * recurring_task.recurrence_interval)

async def process_recurring_tasks():
    """Worker job to create occurrences for due recurring tasks"""
    async with get_db() as db:
        tasks = await db.execute(
            select(RecurringTask)
            .where(RecurringTask.is_active == True)
            .where(RecurringTask.next_due_at <= datetime.utcnow())
        )

        for recurring_task in tasks.scalars():
            # Create new task occurrence
            task = Task(
                user_id=recurring_task.user_id,
                title=recurring_task.title,
                description=recurring_task.description,
                priority=recurring_task.priority,
                recurring_task_id=recurring_task.id
            )
            db.add(task)

            # Update next_due_at
            recurring_task.last_created_at = task.created_at
            recurring_task.next_due_at = calculate_next_due_at(recurring_task)

            await db.commit()
```

**Edge Cases**:
- **End date passed**: Mark is_active=False
- **Task deleted**: Handle gracefully, skip creation
- **User deleted: Clean up all recurring tasks via cascade
- **Missed occurrences**: Backfill on next run or skip (design decision: skip)

**Time Zone Handling**:
- Store all times in UTC in database
- User timezone stored in users table
- Convert to user timezone for notifications
- Schedule jobs based on UTC to avoid confusion

---

## 8. kubectl-ai vs kagent Selection

### Decision: Implement Both for Different Use Cases

**Chosen Approach**: Use kubectl-ai for inline CLI operations, kagent for complex workflows.

**Usage Patterns**:

```bash
# kubectl-ai: Quick CLI operations (inline)
kubectl ai scale deployment backend --replicas=3
kubectl ai get pods -l app=backend --sort-by=.metadata.creationTimestamp
kubectl ai describe pod/backend-xxx --jsonpath='{.spec.containers[*].image}'

# kagent: Complex workflows (interactive)
kagent "Create a new Dapr component for Redis state store"
kagent "Troubleshoot why the notification service pods are crashing"
kagent "Set up monitoring for the todo application"
```

**Rationale**:
- **kubectl-ai**: Faster for simple commands, no context switching
- **kagent**: Better for multi-step operations requiring analysis
- **Complementary**: Both tools can be used in same workflow

**kubectl-ai Configuration**:
```bash
# Install via krew
kubectl krew install ai

# Set OpenAI API key
export OPENAI_API_KEY=sk-...
```

**kagent Configuration**:
```bash
# Install via npm
npm install -g @kagent/cli

# Initialize
kagent init

# Set OpenAI API key
export OPENAI_API_KEY=sk-...
```

---

## 9. Database Migration Strategy for Phase V

### Decision: Incremental Migrations with Backward Compatibility

**Chosen Approach**: Create migration that adds new tables without breaking existing data.

**Migration Steps**:

1. **Create new tables** (no data loss)
2. **Add columns to existing tables** (with defaults)
3. **Create indexes** (non-blocking)
4. **Deploy new services** (feature flagged)
5. **Enable features** (after migration verified)

**Migration File**:
```python
# alembic/versions/005_add_recurring_tasks.py
def upgrade():
    # Create new tables
    op.create_table('recurringtask', ...)
    op.create_table('taskeventlog', ...)

    # Add columns (nullable with defaults)
    op.add_column('tasks', 'due_date', sa.DateTime(), nullable=True)
    op.add_column('tasks', 'notified', sa.Boolean(), server_default='false')

    # Add indexes after data migration
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])

def downgrade():
    # Reverse in reverse order
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_column('tasks', 'notified')
    op.drop_column('tasks', 'due_date')
    op.drop_table('taskeventlog')
    op.drop_table('recurringtask')
```

**Testing Strategy**:
1. Run migration on staging database
2. Verify all existing tests pass
3. Create test data in new tables
4. Run new feature tests
5. Production migration during low-traffic window

---

## 10. Security Considerations for Event-Driven Architecture

### Decision: mTLS for Dapr, RBAC for Kubernetes, Secret Encryption

**Chosen Approach**: Apply defense-in-depth security across all layers.

**Dapr Security**:
```yaml
# Enable mTLS for all Dapr communication
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-trust-bundle
spec:
  trustDomain: "todo-app.local"
  mtls:
    enabled: true
    workloadCertTTL: 3600
    allowedClockSkew: 15m
```

**Kubernetes RBAC**:
```yaml
# Service account for notification service
apiVersion: v1
kind: ServiceAccount
metadata:
  name: notification-service
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: notification-service-role
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: notification-service-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: notification-service-role
subjects:
- kind: ServiceAccount
  name: notification-service
```

**Secret Encryption**:
- Enable encryption at rest for Kubernetes secrets
- Use external secrets manager (AWS Secrets Manager, Azure Key Vault) for production
- Never commit secrets to git

**Network Policies**:
```yaml
# Deny all ingress by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress

# Allow frontend to talk to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: todo-frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: todo-backend
    ports:
    - protocol: TCP
      port: 8000
```

---

## 11. Cost Estimation

### Monthly Cost Breakdown (DOKS Production)

| Component | Quantity | Unit Cost | Monthly |
|-----------|----------|-----------|---------|
| DOKS Cluster | 1 | $60/mo | $60 |
| Load Balancer | 1 | Included | $0 |
| Redpanda Storage | 300Gi | $0.10/GiB | $30 |
| Neon Database | 1 | $29/mo (Postgres 0) | $29 |
| Total | | | **~$120/mo** |

### Complete DigitalOcean Production Cost Breakdown

| DigitalOcean Service | Quantity | Unit Cost | Monthly Cost |
|---------------------|----------|-----------|--------------|
| **DOKS Cluster** | | | |
| ├─ Nodes (s-4vcpu-8gb) | 3 | $20/mo each | $60 |
| ├─ Control Plane | 1 | Free | $0 |
| **Load Balancers** | 3 | $12/mo each | $36 |
| **Managed Redis (Valkey)** | 1GB Basic | $15/mo | $15 |
| **Block Storage** | 3× 50GB | $0.10/GB | $12 |
| **Container Registry** | ~5GB | ~$5/mo | $5 |
| **Cloud Firewalls** | Included | Free | $0 |
| **Bandwidth** | Included (with LB) | Free | $0 |
| **Neon Database** | 1 | $29/mo | $29 |
| **TOTAL** | | | **~$157/mo** |

**Note**: The DO Container Registry cost is approximately $5/mo for 5GB storage. Bandwidth is included with Load Balancers up to fair usage limits.

### Cost Optimization Options

| Optimization | Monthly Savings | Trade-off |
|--------------|------------------|-----------|
| Use 2 nodes instead of 3 | $20/mo | Less redundancy, slower recovery |
| Use single LB + Ingress | $24/mo | More complex routing config |
| Use Minikube for testing | $128/mo | No production-like environment |
| Scale to 2 nodes during off-hours | Variable | ~10 min scale-up time |

### Cost Comparison: DigitalOcean vs Alternatives

| Component | DigitalOcean | Google Cloud (GKE) | Azure (AKS) |
|-----------|--------------|-------------------|-------------|
| **Kubernetes Cluster** | | | |
| Nodes (3× 4vCPU/8GB) | $60/mo | ~$90/mo | ~$75/mo |
| Control Plane | Free | $74/mo | $0 |
| **Load Balancers** (3×) | $36/mo | ~$54/mo | ~$54/mo |
| **Block Storage** (150GB) | $12/mo | $6/mo | $7.50/mo |
| **Managed Redis** | $15/mo | ~$25/mo | ~$20/mo |
| **Container Registry** | ~$5/mo | Free tier, then ~$7/mo | ~$5/mo |
| **Database** (Neon) | $29/mo | $29/mo (external) | $29/mo (external) |
| **TOTAL** | **~$157/mo** | **~$285/mo** | **~$190/mo** |

**Conclusion**: DigitalOcean is approximately **45% cheaper** than GKE and **17% cheaper** than AKS for this workload.

### Additional Costs (Optional)
- GitHub Actions: Free for public repos
- Domain name: $12/year via DO or external registrar
- SSL Certificates: Free (Let's Encrypt via cert-manager)
- Monitoring: Free (self-hosted Prometheus + Grafana)
- Backup/Disaster Recovery: Additional $10-20/mo for DO snapshots

### Free Development Alternatives
For testing without costs:
- **Minikube**: Local Kubernetes (free)
- **Kind**: Kubernetes in Docker (free)
- **K3d**: Lightweight Kubernetes (free)

**Recommendation**: Use DigitalOcean for production deployment due to cost-effectiveness and simplicity. The $157/mo cost is reasonable for a production-grade event-driven microservices application.

---

## 12. Performance Baselines

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p50) | <200ms | Prometheus histogram |
| API Response Time (p95) | <500ms | Prometheus histogram |
| API Response Time (p99) | <1000ms | Prometheus histogram |
| Event Latency | <100ms | Dapr metrics |
| Notification Delivery | <5 seconds | Custom metric |
| Pod Startup Time | <30s | Kubernetes metrics |
| Database Query Time | <50ms | PostgreSQL pg_stat_statements |

### Scalability Targets
- Concurrent Users: 1,000+
- Tasks Created per Day: 10,000+
- Events per Second: 100+
- Recurring Tasks: 1,000+

---

## 13. Rollback Strategy

### Decision: Helm Native Rollback + Blue-Green Deployments

**Rollback Commands**:
```bash
# Rollback to previous Helm release
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app --revision 5

# Rollback and pin version
helm rollback todo-app && \
  helm upgrade todo-app ./helm/todo-app \
    --set image.tag=previous-sha
```

**Blue-Green Deployment**:
```yaml
# Deploy to green (inactive)
helm install todo-app-green ./helm/todo-app \
  --set image.tag=${{ github.sha }} \
  --namespace production

# Wait for green ready
kubectl wait --for=condition=ready pod -l app=todo-app-green

# Switch service selector
kubectl patch service todo-app \
  -p '{"spec":{"selector":{"app":"todo-app-green"}}}'

# Clean up blue
helm uninstall todo-app
```

**Rollback Triggers**:
- Health check fails
- Error rate >5%
- P99 latency >2s
- Database connection failures

---

## 14. Testing Strategy

### Unit Tests
- Recurring task calculation logic
- Event serialization/deserialization
- Dapr client mocking

### Integration Tests
- Event publishing to Kafka
- Event subscription and processing
- End-to-end task flow with due dates

### Load Tests
- Locust/K6 simulating 1000 users
- Event throughput testing (100 events/sec)
- Database query performance under load

### E2E Tests
- Create recurring task → verify daily occurrence
- Create task with due date → verify notification
- Complete task → verify event published
- Scale deployment → verify no data loss

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Orchestration | Kubernetes | 1.29+ |
| Container Runtime | containerd | Built-in |
| Service Mesh | Dapr | 1.12+ |
| Event Streaming | Redpanda | Latest |
| CI/CD | GitHub Actions | - |
| Monitoring | Prometheus + Grafana | Latest |
| Logging | Loki (optional) | Latest |
| Database | Neon PostgreSQL | 16 |
| Language | Python | 3.13 |
| Frontend | Next.js | 14 |
| Ingress | Nginx | - |
| Package Manager | Helm | 3.0+ |
