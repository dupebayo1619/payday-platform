🚀 Payday DevOps Platform

Production-Grade Fintech Platform on AWS EKS with GitOps, Observability, Security & Disaster Recovery


Built by Adebayo Modupeoluwa (Member C - GitOps & App Developer)
Team:Payday DevOps Team (Members A-F)
Duration:10-day sprint | AWS EKS | GitOps

-📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Infrastructure Setup](#infrastructure-setup)
- [Application Deployment](#application-deployment)
- [GitOps with Argo CD](#gitops-with-argo-cd)
- [Observability](#observability)
- [Security](#security)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Autoscaling](#autoscaling)
- [Project Structure](#project-structure)
- [Key Commands](#key-commands)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)

🎯 Project Overview

Payday DevOps Platform is a fully automated, production-grade software delivery system built on AWS EKS. It transforms how the fictional Payday startup (a Nigerian fintech company) deploys software — from manual, error-prone releases to fully automated, self-healing, observable, and secure GitOps workflows.

Business Problem Solved

Before this platform:

- ❌ Frequent deployment failures (33% of deployments caused incidents)
- ❌ Inconsistent environments ("it works on my machine" problem)
- ❌ Manual rollbacks taking 2-3 hours
- ❌ No security scanning — CVEs reaching production
- ❌ Zero observability — SSH + grep debugging



After this platform:
- ✅ Zero-touch CI/CD pipeline (test → build → scan → deploy)
- ✅ GitOps with Argo CD (Git as single source of truth)
- ✅ Canary rollouts + 47-second rollbacks
- ✅ Trivy vulnerability scanning (blocks CVEs)
- ✅ Prometheus + Grafana + Loki (complete observability)
- ✅ Velero backups (4m 23s restore, zero data loss)

🏗️ Architecture

High-Level Architecture

┌─────────────────────────────────────────────────────────────────────────────┐
│                              GITHUB REPOSITORY                               │
│                         (Single Source of Truth)                             │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS (CI/CD)                               │
│  Test → Build → Trivy Scan → Push to ECR → Update Helm Values               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ARGO CD (GitOps)                                │
│                    Monitors Git → Auto-syncs to Cluster                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS EKS KUBERNETES                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         NAMESPACE: staging                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │   │
│  │  │Frontend  │ │  API     │ │ Worker   │ │PostgreSQL│              │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        NAMESPACE: production                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │   │
│  │  │Frontend 3│ │  API 3   │ │ Worker 2 │ │PostgreSQL│              │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    NAMESPACE: monitoring                             │   │
│  │  Prometheus │ Grafana │ Loki │ Alertmanager                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

| Service     | Technology              | Description                                                                 |
|-------------|-------------------------|-----------------------------------------------------------------------------|
| Frontend    | Nginx + React           | SPA dashboard, polls API every 30s, displays payment records               |
| API         | Python 3.12 + Flask     | REST endpoints: `/health`, `/payments`, `/metrics` (Prometheus)            |
| Worker      | Python background       | Runs every 10s, processes pending payments                                 |
| Database    | PostgreSQL 15           | StatefulSet with 5GB EBS persistent volume      



| Category         | Tools                                                                 |
|------------------|-----------------------------------------------------------------------|
| Cloud            | AWS (EKS, ECR, S3, VPC)                                               |
| IaC              | Terraform                                                             |
| Container        | Docker                                                                |
| Orchestration    | Kubernetes 1.29                                                       |
| CI/CD            | GitHub Actions                                                        |
| GitOps           | Argo CD + Argo Rollouts                                               |
| Observability    | Prometheus, Grafana, Loki, OpenTelemetry                              |
| Security         | Trivy, HashiCorp Vault, NetworkPolicies                               |
| Backup           | Velero (S3 backend)                                                   |
| Autoscaling      | HPA + KEDA                                                            |
| Languages        | Python 3.12, JavaScript (React)                                       |



Prerequisites
Required Tools

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./awscliv2/install

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Argo CD CLI
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd && sudo mv argocd /usr/local/bin/

# Velero
curl -LO https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz && sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/


AWS Resources Required
AWS account with billing enabled

IAM user with AdministratorAccess (for the project duration)

Default VPC or custom VPC with public/private subnets

🚀 Quick Start

1. Clone the Repository

git clone https://github.com/payday-devops-team/payday-platform.git
cd payday-platform

2. Provision Infrastructure with Terraform
cd infra/terraform
terraform init
terraform plan
terraform apply -auto-approve

3. Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name payday-eks
kubectl get nodes

4. Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n argocd --timeout=300s

# Port forward Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443 &

5. Deploy the Application
# Create namespaces
kubectl create namespace staging
kubectl create namespace production

# Apply Argo CD applications
kubectl apply -f environments/staging/application.yaml
kubectl apply -f environments/production/application.yaml

6. Access the Application
# Port forward to staging
kubectl port-forward svc/payday-frontend -n staging 3000:80

# Port forward to production
kubectl port-forward svc/payday-frontend -n production 3001:80


Open http://localhost:3000 (staging) or http://localhost:3001 (production)


🏗️ Infrastructure Setup

Terraform Resources
All infrastructure is defined in infra/terraform/:

# main.tf
- VPC with 2 public + 2 private subnets
- NAT Gateway for private subnet internet access
- EKS Cluster (Kubernetes 1.29)
- Node Group (2× t3.small, min=1, max=5)
- ECR Repositories (frontend, api, worker)
- S3 Bucket for Velero backups
- IAM Roles for EKS, Velero, GitHub Actions


Provision Infrastructure

cd infra/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply infrastructure
terraform apply -auto-approve

# Destroy infrastructure (end of project)
terraform destroy -auto-approve


📦 Application Deployment

payday-app/
├── frontend/                  # React + Nginx frontend
│   ├── src/                   # React components
│   ├── public/                # Static assets
│   ├── Dockerfile             # Multi-stage build
│   └── nginx.conf             # Nginx configuration
├── api/                       # Python Flask API
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Python slim image
├── worker/                    # Background worker
│   ├── worker.py              # Payment processor
│   ├── requirements.txt
│   └── Dockerfile
├── postgres/                  # Database
│   └── init.sql               # Schema + seed data
└── db-init.sql               # Database initialization script


Build and Push Images Manually

# Frontend
cd frontend
docker build -t payday-frontend:latest .
docker tag payday-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/payday/frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/payday/frontend:latest

# API
cd ../api
docker build -t payday-api:latest .
docker tag payday-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/payday/api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/payday/api:latest

# Worker
cd ../worker
docker build -t payday-worker:latest .
docker tag payday-worker:latest <account>.dkr.ecr.us-east-1.amazonaws.com/payday/worker:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/payday/worker:latest

🔄 GitOps with Argo CD

# environments/staging/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payday-staging
spec:
  source:
    repoURL: https://github.com/payday-devoops-team/payday-platform
    targetRevision: master
    path: payday-app/payday-chart
    helm:
      values: |
        namespace: staging
        frontend:
          replicas: 1
          tag: latest
        api:
          replicas: 1
        worker:
          replicas: 1
  destination:
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

Helm Chart Structure

payday-chart/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
└── templates/
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── api-deployment.yaml
    ├── api-service.yaml
    ├── worker-deployment.yaml
    ├── postgres-statefulset.yaml
    ├── postgres-service.yaml
    └── postgres-pvc.yaml

Common Argo CD Commands

# List applications
argocd app list

# Check sync status
argocd app get payday-staging

# Sync application manually
argocd app sync payday-staging

# Rollback to previous version
argocd app rollback payday-production 1

# Watch sync progress
argocd app get payday-staging --watch

📊 Observability

Prometheus + Grafana

# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Port forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Access Grafana: http://localhost:3000
# Username: admin
# Password: prom-operator

Loki Logging

# Install Loki
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true

# Add Loki as data source in Grafana
# URL: http://loki.monitoring.svc.cluster.local:3100



Key Dashboards

| Dashboard             | Description                                  | Dashboard ID |
|-----------------------|----------------------------------------------|--------------|
| SLO Dashboard         | Error rate, latency, availability            | Custom       |
| Kubernetes Cluster    | CPU, memory, network                         | 315          |
| Node Exporter         | Node-level metrics                           | 1860         |
| API Performance       | Request rate, latency by endpoint            | Custom       |



🔒 Security

Trivy Image Scanning
GitHub Actions pipeline includes Trivy scanning:

- name: Scan image with Trivy
  run: |
    trivy image --severity CRITICAL,HIGH --exit-code 1 ${{ steps.build.outputs.image }}


HashiCorp Vault

# Install Vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm upgrade --install vault hashicorp/vault \
  --namespace vault --create-namespace

# Initialize Vault
kubectl exec -n vault vault-0 -- vault operator init

# Store database password
kubectl exec -n vault vault-0 -- vault kv put secret/payday/db password=securepassword

Network Policies

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-network-policy
spec:
  podSelector:
    matchLabels:
      app: postgres
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    - podSelector:
        matchLabels:
          app: worker
    ports:
    - port: 5432

💾 Backup & Disaster Recovery

# Install Velero
velero install \
  --provider aws \
  --bucket payday-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --plugins velero/velero-plugin-for-aws:v1.8.0

Backup Commands

# Schedule nightly backup
velero schedule create nightly-backup \
  --schedule="0 1 * * *" \
  --include-namespaces staging,production

# Manual backup
velero backup create demo-backup \
  --include-namespaces staging

# List backups
velero backup get

# Restore from backup
velero restore create --from-backup demo-backup

# Check restore status
velero restore describe demo-backup


Restore Procedure (Tested)
Backup time: 4 minutes 23 seconds

Data loss: Zero (all 20 payment records recovered)

Process: Delete namespace → Velero restore → All resources restored

⚡ Autoscaling

Horizontal Pod Autoscaler (HPA)

# Configure HPA for API
kubectl autoscale deployment api \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n production

# Check HPA status
kubectl get hpa -n production -w

KEDA Event-Driven Autoscaling

apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: worker-scaledobject
spec:
  scaleTargetRef:
    name: worker
  triggers:
  - type: postgresql
    metadata:
      query: "SELECT COUNT(*) FROM payments WHERE status = 'pending'"
      targetQueryValue: "10"





📁 Project Structure

payday-platform/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI/CD pipeline
│       └── trivy-scan.yml           # Security scanning
├── infra/
│   └── terraform/
│       ├── main.tf                   # EKS cluster
│       ├── variables.tf
│       └── outputs.tf
├── payday-app/
│   ├── frontend/
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── api/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── worker/
│   │   ├── worker.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── postgres/
│   │   └── init.sql
│   ├── payday-chart/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── db-init.sql
├── environments/
│   ├── staging/
│   │   └── application.yaml
│   └── production/
│       └── application.yaml
├── monitoring/
│   ├── prometheus-values.yaml
│   ├── grafana-values.yaml
│   └── loki-values.yaml
├── security/
│   ├── vault-values.yaml
│   └── network-policies.yaml
├── backup/
│   └── velero-schedule.yaml
└── docs/
    ├── runbooks/
    └── architecture-diagrams/


⌨️ Key Commands Reference

Cluster Management
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name payday-eks

# Check nodes
kubectl get nodes

# Check pods across namespaces
kubectl get pods -A

# Check resources in namespace
kubectl get all -n production

Argo CD
# Port forward UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Login
argocd login localhost:8080 --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

# Sync application
argocd app sync payday-staging

# Get application details
argocd app get payday-production


Argo Rollouts
# Watch canary rollout
kubectl argo rollouts get rollout api -n production --watch

# Promote canary
kubectl argo rollouts promote api -n production

# Rollback
kubectl argo rollouts undo api -n production


Observability
# Port forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Port forward Prometheus
kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090

# Access API metrics
kubectl port-forward svc/payday-api -n production 5000:5000
curl http://localhost:5000/metrics


Velero Backup/Restore
# Create backup
velero backup create demo-backup --include-namespaces staging

# List backups
velero backup get

# Restore
velero restore create --from-backup demo-backup

# Check restore status
velero restore describe demo-backup


HPA & Scaling
# Get HPA status
kubectl get hpa -n production

# Scale node group to 0 (save costs)
eksctl scale nodegroup --cluster=payday-eks --name=default --nodes=0

# Scale pods manually
kubectl scale deployment api --replicas=5 -n production



🔧 Troubleshooting

Common Issues & Solutions

| Issue                                | Solution                                                                                |
|--------------------------------------|-----------------------------------------------------------------------------------------|
| EKS cluster creation fails           | Check IAM permissions; ensure AdministratorAccess policy is attached                    |
| Argo CD cannot access GitHub         | Add GitHub PAT: `argocd repo add <URL> --username <user> --password <PAT>`              |
| Trivy scan fails                     | Update vulnerable dependencies in `requirements.txt`                                    |
| Grafana cannot reach Loki            | Use full DNS: `http://loki.monitoring.svc.cluster.local:3100`                           |
| Velero restore missing data          | Install EBS CSI driver and VolumeSnapshotClass                                          |
| Pod stuck in Pending                 | Check node capacity: `kubectl describe nodes`                                           |
| ImagePullBackOff                     | Verify image name, tag, and registry credentials; check imagePullSecrets                |


Debugging Commands

# Check pod logs
kubectl logs -n production deployment/api --tail=100

# Describe pod for events
kubectl describe pod -n production <pod-name>

# Check pod status
kubectl get pods -n production -w

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward svc/payday-api -n production 5000:5000

👥 Contributors

| Member      | Role                      | Responsibilities                                                                 |
|-------------|---------------------------|----------------------------------------------------------------------------------|
| Member A    | Infrastructure Lead       | Terraform EKS, VPC, ECR, S3, namespaces, RBAC                                    |
| Member B    | CI/CD Engineer            | GitHub Actions pipeline, Trivy scanning, ECR push                                |
| Member C    | GitOps & App Developer    | Application code, Dockerfiles, Argo CD, Helm charts                              |
| Member D    | Observability Engineer    | Prometheus, Grafana, Loki, alerts, runbooks                                      |
| Member E    | Security & DR             | HashiCorp Vault, Velero backups, NetworkPolicies                                 |
| Member F    | Helm, Autoscaling & Cost  | HPA, KEDA, ResourceQuotas, cost documentation                                    |



📄 License

This project is for educational purposes as part of a DevOps engineering coursework

🙏 Acknowledgements

Kubernetes open source community

Argo CD & Argo Rollouts maintainers

Prometheus, Grafana, and Loki teams

HashiCorp Vault team

Velero contributors

AWS documentation team

🔗 Useful Links


Kubernetes Documentation
https://kubernetes.io/docs

Argo CD Documentation
https://argo-cd.readthedocs.io/

Prometheus Operator
https://prometheus-operator.dev/

Grafana Loki
https://grafana.com/oss/loki

HashiCorp Vault
https://developer.hashicorp.com/vault/docs

Velero Documentation
https://developer.hashicorp.com/vault/docs

Trivy Documentation
https://aquasecurity.github.io/trivy


Terraform AWS Provider
https://registry.terraform.io/providers/hashicorp/aws


📊 Project Status

| Metric                    | Value                                                |
|---------------------------|------------------------------------------------------|
| Project Duration          | 10 working days (1.5 weeks)                         |
| Services Deployed         | 5 (Frontend, API, Worker, PostgreSQL, Redis)        |
| Production Replicas       | 3 Frontend, 3 API, 2 Worker                         |
| Total AWS Cost            | ~$12-18 USD                                          |
| Pipeline Duration         | ~4 minutes                                           |
| GitOps Sync Time          | < 3 minutes                                          |
| Rollback Time             | 47 seconds                                           |
| Restore Time              | 4 minutes 23 seconds                                 |
| Error Rate (steady)       | 0.00%                                                |
| P99 Latency               | ~42ms                                                |



✅ Final Checklist

Terraform provisions EKS cluster successfully

GitHub Actions CI/CD pipeline passes all tests

Trivy security scan blocks CVEs

Argo CD syncs automatically on Git push

Canary rollouts work with Argo Rollouts

Rollback completes in < 2 minutes

Prometheus scrapes metrics from all pods

Grafana displays SLO dashboard

Loki aggregates logs from all services

Vault stores database secrets

Velero backup and restore tested (zero data loss)

HPA autoscales based on CPU

KEDA scales worker based on queue depth

All 6 team members contributed

