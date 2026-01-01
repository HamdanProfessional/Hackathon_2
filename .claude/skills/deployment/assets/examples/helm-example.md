# Helm Chart Example

## Chart Structure

```
helm/todo-app/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── secrets.yaml
```

## Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: A Helm chart for Todo application
type: application
version: 1.0.0
appVersion: "1.0"
```

## values.yaml

```yaml
replicaCount: 3

image:
  repository: registry.digitalocean.com/todo-backend
  pullPolicy: Always
  tag: "latest"

service:
  type: LoadBalancer
  port: 80

env:
  databaseUrl: ""
  secretKey: ""

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
```

## deployment.yaml Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: {{ .Values.env.databaseUrl | quote }}
        - name: SECRET_KEY
          value: {{ .Values.env.secretKey | quote }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

## Install/Upgrade

```bash
# Install
helm install todo-app ./helm/todo-app -n production --create-namespace

# Upgrade
helm upgrade todo-app ./helm/todo-app -n production

# Uninstall
helm uninstall todo-app -n production
```
