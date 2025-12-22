# Kubernetes Quick Reference Card

## Helm Commands

### Install/Upgrade
```bash
helm install <release> <chart>
helm install <release> <chart> -f values.yaml
helm upgrade <release> <chart> -f values.yaml
helm uninstall <release>
```

### Status & Info
```bash
helm list
helm status <release>
helm history <release>
helm get all <release>
helm get values <release>
```

### Lint & Test
```bash
helm lint <chart>
helm template <chart>
helm test <release>
```

### Repository
```bash
helm repo add <name> <url>
helm repo update
helm search repo <keyword>
```

## kubectl Commands

### Cluster Info
```bash
kubectl cluster-info
kubectl version
kubectl config current-context
kubectl config get-contexts
```

### Resources - Get
```bash
kubectl get all
kubectl get pods
kubectl get services
kubectl get deployments
kubectl get ingress
kubectl get secrets
kubectl get configmaps

# Get with more details
kubectl get pods -o wide
kubectl get pods -o yaml

# Get by label
kubectl get pods -l app=frontend
kubectl get all -l app.kubernetes.io/name=backend
```

### Resources - Describe
```bash
kubectl describe pod <pod-name>
kubectl describe svc <service-name>
kubectl describe deployment <deployment-name>
```

### Logs
```bash
kubectl logs <pod-name>
kubectl logs <pod-name> --tail=50
kubectl logs <pod-name> -f
kubectl logs -l app=frontend --tail=100 -f

# Previous container logs
kubectl logs <pod-name> --previous
```

### Exec
```bash
kubectl exec -it <pod-name> -- sh
kubectl exec -it <pod-name> -- bash
kubectl exec <pod-name> -- ls -la /app
kubectl exec <pod-name> -- env
```

### Port Forward
```bash
kubectl port-forward pod/<pod-name> 8080:3000
kubectl port-forward svc/<service-name> 8080:80
kubectl port-forward deployment/<deployment-name> 8080:3000
```

### Scale
```bash
kubectl scale deployment/<name> --replicas=3
kubectl scale statefulset/<name> --replicas=5
```

### Rollout
```bash
kubectl rollout restart deployment/<name>
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2
```

### Apply/Delete
```bash
kubectl apply -f manifest.yaml
kubectl apply -f k8s/
kubectl delete -f manifest.yaml
kubectl delete pod <pod-name>
kubectl delete svc <service-name>
kubectl delete deployment <deployment-name>
```

### Edit
```bash
kubectl edit pod <pod-name>
kubectl edit svc <service-name>
kubectl edit configmap <configmap-name>
```

## Minikube Commands

### Start/Stop
```bash
minikube start
minikube start --cpus=4 --memory=8192
minikube stop
minikube delete
```

### Status
```bash
minikube status
minikube ip
minikube profile list
```

### Service Access
```bash
minikube service <service-name>
minikube service <service-name> --url
minikube tunnel  # Runs in background for LoadBalancer
```

### Images
```bash
minikube image load <image-name>
minikube image ls
minikube image rm <image-name>
```

### Dashboard
```bash
minikube dashboard
```

### Addons
```bash
minikube addons list
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons disable ingress
```

## Pod Management

### Common Pod States
- `Pending`: Pod scheduled but not running yet
- `Running`: Pod is running
- `Succeeded`: Pod completed successfully
- `Failed`: Pod exited with error
- `CrashLoopBackOff`: Pod keeps crashing
- `ImagePullBackOff`: Image pull failed

### Debug Pods
```bash
# Get pod events
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>

# Get previous logs if pod restarted
kubectl logs <pod-name> --previous

# Execute into pod
kubectl exec -it <pod-name> -- sh

# Check pod resources
kubectl top pods
kubectl top pod <pod-name> --containers
```

### Delete Pods
```bash
kubectl delete pod <pod-name>
kubectl delete pods -l app=frontend
kubectl delete pods --all
kubectl delete pods --force --grace-period=0
```

## Service Types

### NodePort
```bash
# Access via <NodeIP>:<NodePort>
minikube ip  # Get NodeIP
kubectl get svc <name>  # Get NodePort
```

### LoadBalancer (Minikube)
```bash
# Start tunnel first
minikube tunnel

# Get external IP
kubectl get svc <name>
```

### ClusterIP
```bash
# Only accessible within cluster
# Use port-forward to access locally
kubectl port-forward svc/<name> 8080:80
```

## ConfigMaps & Secrets

### ConfigMaps
```bash
kubectl create configmap <name> --from-literal=key=value
kubectl create configmap <name> --from-file=file.txt
kubectl get configmaps
kubectl describe configmap <name>
kubectl edit configmap <name>
kubectl delete configmap <name>
```

### Secrets
```bash
kubectl create secret generic <name> --from-literal=key=value
kubectl create secret generic <name> --from-file=file.txt
kubectl get secrets
kubectl describe secret <name>
kubectl edit secret <name>
kubectl delete secret <name>

# Decode secret value
kubectl get secret <name> -o jsonpath='{.data.key}' | base64 -d
```

## Namespaces

```bash
kubectl create namespace <name>
kubectl get namespaces
kubectl config set-context --current --namespace=<name>
kubectl delete namespace <name>

# Get resources in namespace
kubectl get all -n <namespace>
```

## YAML Examples

### Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: myapp
spec:
  containers:
  - name: container
    image: nginx:latest
    ports:
    - containerPort: 80
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
  type: NodePort
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: container
        image: nginx:latest
        ports:
        - containerPort: 80
```

## Useful Aliases (add to .bashrc/.zshrc)

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kdp='kubectl describe pod'
alias kds='kubectl describe service'
alias klf='kubectl logs -f'
alias ket='kubectl exec -it'
alias kaf='kubectl apply -f'
```

## Troubleshooting

### Check Resource Usage
```bash
kubectl top nodes
kubectl top pods
kubectl top pods -l app=frontend
```

### Get Pod IP
```bash
kubectl get pod <pod-name> -o jsonpath='{.status.podIP}'
```

### Get Service Endpoints
```bash
kubectl get endpoints <service-name>
```

### Port Forward to Debug
```bash
kubectl port-forward <pod-name> 8080:80
# Then access http://localhost:8080
```

### Copy Files to/from Pod
```bash
kubectl cp ./local-file.txt <pod-name>:/app/remote-file.txt
kubectl cp <pod-name>:/app/remote-file.txt ./local-file.txt
```
