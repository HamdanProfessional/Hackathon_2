---
id: 006
title: "helm charts implementation"
stage: red
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-kubernetes
branch: 004-kubernetes
user: Hamdan
command: implement helm charts
labels: ["implementation", "helm", "kubernetes", "charts", "phase4"]
links:
  spec: specs/004-kubernetes/spec.md
  plan: specs/004-kubernetes/plan.md
  tasks: specs/004-kubernetes/tasks.md
  contract: specs/004-kubernetes/contracts/kubernetes-resources.md
  ticket: null
  adr: null
  pr: null
files:
  - helm/frontend/Chart.yaml
  - helm/frontend/values.yaml
  - helm/frontend/templates/deployment.yaml
  - helm/frontend/templates/service.yaml
  - helm/frontend/templates/configmap.yaml
  - helm/frontend/templates/ingress.yaml
  - helm/frontend/templates/hpa.yaml
  - helm/frontend/templates/_helpers.tpl
  - helm/frontend/templates/NOTES.txt
  - helm/backend/Chart.yaml
  - helm/backend/values.yaml
  - helm/backend/templates/deployment.yaml
  - helm/backend/templates/service.yaml
  - helm/backend/templates/secrets.yaml
  - helm/backend/templates/configmap.yaml
  - helm/backend/templates/ingress.yaml
  - helm/backend/templates/hpa.yaml
  - helm/backend/templates/_helpers.tpl
  - helm/backend/templates/NOTES.txt
tests:
  - Both Helm charts created
  - All templates render correctly
  - helm lint passes
  - Security context configured
  - Resource limits defined
---

## Prompt

Implement Phase 3 & 4: Helm Charts

Create production-ready Helm charts for both frontend and backend with all required templates, security hardening, and documentation.

REQUIREMENTS:

**Frontend Chart** (`helm/frontend/`):
- Chart.yaml: API version v2, name todo-frontend
- values.yaml: Image, service, ingress, resources, HPA config
- Templates:
  - deployment.yaml: 2 replicas, security context, resource limits
  - service.yaml: NodePort 30001 (or LoadBalancer)
  - configmap.yaml: NEXT_PUBLIC_API_URL
  - ingress.yaml: Optional ingress for domain routing
  - hpa.yaml: Horizontal Pod Autoscaler
  - _helpers.tpl: Template helpers
  - NOTES.txt: Post-install instructions

**Backend Chart** (`helm/backend/`):
- Chart.yaml: API version v2, name todo-backend
- values.yaml: Image, service, ingress, secrets, config, resources, HPA config
- Templates:
  - deployment.yaml: 2 replicas, security context, resource limits
  - service.yaml: NodePort 30002 (or LoadBalancer)
  - secrets.yaml: Database URL, JWT, API keys
  - configmap.yaml: CORS, app settings
  - ingress.yaml: Optional ingress for API routing
  - hpa.yaml: Horizontal Pod Autoscaler
  - _helpers.tpl: Template helpers
  - NOTES.txt: Post-install instructions

**Security Requirements**:
- runAsNonRoot: true
- runAsUser: 1001
- allowPrivilegeEscalation: false
- capabilities.drop: [ALL]
- Resource requests and limits

## Response snapshot

Successfully created complete Helm charts for both frontend and backend with all required templates.

### Files Created (17 total):

**Frontend Chart (9 files)**:
- Chart.yaml - Helm chart metadata
- values.yaml - Configuration values
- templates/deployment.yaml - 2 replicas, security context
- templates/service.yaml - NodePort 30001
- templates/configmap.yaml - NEXT_PUBLIC_API_URL
- templates/ingress.yaml - Optional ingress
- templates/hpa.yaml - Horizontal Pod Autoscaler
- templates/_helpers.tpl - Template helpers
- templates/NOTES.txt - Post-install instructions

**Backend Chart (9 files)**:
- Chart.yaml - Helm chart metadata
- values.yaml - Configuration values with secrets
- templates/deployment.yaml - 2 replicas, security context
- templates/service.yaml - NodePort 30002
- templates/secrets.yaml - Database URL, JWT, API keys
- templates/configmap.yaml - CORS, app settings
- templates/ingress.yaml - Optional ingress
- templates/hpa.yaml - Horizontal Pod Autoscaler
- templates/_helpers.tpl - Template helpers
- templates/NOTES.txt - Post-install instructions

### Security Features Implemented:

**Frontend values.yaml**:
```yaml
podSecurityContext:
  fsGroup: 1001

securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Backend values.yaml**:
```yaml
podSecurityContext:
  fsGroup: 1001
  runAsNonRoot: true

securityContext:
  runAsUser: 1001
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL

resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Helm Lint Results:
```
==> Linting helm/frontend
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed

==> Linting helm/backend
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed
```

## Outcome

- ✅ Impact: Production-ready Helm charts created
- 🧪 Tests: Both charts pass helm lint, all templates render
- 📁 Files: 18 files created (2 charts × 9 files)
- 🔁 Next prompts: Create deployment documentation
- 🧠 Reflection: Complete Helm charts ready for Minikube and cloud deployment

## Evaluation notes (flywheel)

- Failure modes observed: None - all charts lint successfully
- Graders run and results (PASS/FAIL): PASS - Helm charts valid
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with `helm template` and `helm install`
