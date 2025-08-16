# GCP Deployment Guide - Qdrant Search Application

## 🎯 **GCP Cluster Sizing Recommendations**

### **Resource Requirements Summary:**
- **Memory**: 4-8GB (ML models + application)
- **CPU**: 2-4 vCPU (inference + processing)
- **Storage**: 20-50GB (models + data)
- **Network**: Moderate (API requests)

---

## 🚀 **GCP Deployment Options**

### **Option 1: Compute Engine (Recommended)**

#### **Machine Type Recommendations:**

##### **Development/Testing:**
```
Machine: e2-micro
- vCPU: 2 (shared)
- Memory: 1GB
- Cost: ~$6-8/month
- Suitability: ⚠️ Limited (may need e2-small)
```

##### **Small Production (Recommended):**
```
Machine: e2-medium
- vCPU: 2 (shared)
- Memory: 4GB
- Cost: ~$24-30/month
- Suitability: ✅ Good for small workloads
```

##### **Medium Production:**
```
Machine: e2-standard-2
- vCPU: 2 (shared)
- Memory: 8GB
- Cost: ~$48-60/month
- Suitability: ✅ Excellent for medium workloads
```

##### **High Performance:**
```
Machine: c2-standard-4
- vCPU: 4 (dedicated)
- Memory: 16GB
- Cost: ~$120-150/month
- Suitability: ✅ High throughput
```

### **Option 2: Google Kubernetes Engine (GKE)**

#### **Cluster Sizing:**

##### **Small Cluster (Recommended):**
```
Node Pool: e2-medium
- Nodes: 1-2
- vCPU per node: 2
- Memory per node: 4GB
- Cost: ~$30-60/month
- Suitability: ✅ Good for containerized deployment
```

##### **Medium Cluster:**
```
Node Pool: e2-standard-2
- Nodes: 2-3
- vCPU per node: 2
- Memory per node: 8GB
- Cost: ~$60-120/month
- Suitability: ✅ Excellent for scaling
```

### **Option 3: Cloud Run (Serverless)**

#### **Container Configuration:**
```
Memory: 4GB
CPU: 2 vCPU
Concurrency: 80
Cost: ~$40-80/month (pay per request)
Suitability: ⚠️ Limited (cold starts for ML models)
```

---

## 🎯 **Recommended GCP Setup**

### **Best Choice: Compute Engine with e2-medium**

#### **Configuration:**
```
Machine Type: e2-medium
- vCPU: 2
- Memory: 4GB
- Boot Disk: 20GB (Standard Persistent Disk)
- Region: us-central1 (or your preferred region)
- Cost: ~$25-30/month
```

#### **Why This Works:**
✅ **Memory**: 4GB sufficient for ML models
✅ **CPU**: 2 vCPU handles inference well
✅ **Cost**: Very affordable
✅ **Scalability**: Easy to upgrade
✅ **Reliability**: High uptime SLA

---

## 📋 **Step-by-Step GCP Deployment**

### **Step 1: Create Compute Engine Instance**

```bash
# Create instance with Docker
gcloud compute instances create qdrant-search-app \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#! /bin/bash
    # Update system
    apt-get update
    apt-get install -y docker.io docker-compose git
    
    # Start Docker
    systemctl start docker
    systemctl enable docker
    
    # Clone repository
    git clone https://github.com/yourusername/faissGrocerEase.git /app
    cd /app
    
    # Start services
    docker-compose up -d db qdrant
    sleep 30
    docker-compose up -d app
    docker-compose exec app python -m scripts.ingest_products_qdrant'
```

### **Step 2: Configure Firewall Rules**

```bash
# Allow HTTP traffic
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# Allow API traffic
gcloud compute firewall-rules create allow-api \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

### **Step 3: Deploy Application**

```bash
# SSH into instance
gcloud compute ssh qdrant-search-app --zone=us-central1-a

# Check services
docker-compose ps

# Test API
curl -X GET "http://localhost:8000/"

# Test search
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "electronics", "lat": 0.0, "lon": 0.0, "radius_km": 10000.0, "max_results": 3}'
```

---

## 🔧 **GCP-Specific Optimizations**

### **1. Use Cloud Storage for Models**
```python
# Store ML models in Cloud Storage
from google.cloud import storage

def download_model():
    storage_client = storage.Client()
    bucket = storage_client.bucket('your-model-bucket')
    blob = bucket.blob('all-MiniLM-L6-v2')
    blob.download_to_filename('/app/models/all-MiniLM-L6-v2')
```

### **2. Cloud SQL for Database**
```yaml
# Use Cloud SQL instead of containerized PostgreSQL
services:
  app:
    environment:
      - POSTGRES_HOST=/cloudsql/your-project:us-central1:your-instance
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_DB=grocerease
```

### **3. Cloud Run for API (Alternative)**
```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: qdrant-search-api
spec:
  template:
    spec:
      containers:
      - image: gcr.io/your-project/qdrant-search-app
        resources:
          limits:
            memory: 4Gi
            cpu: 2
        env:
        - name: POSTGRES_HOST
          value: "your-cloudsql-connection"
```

---

## 💰 **GCP Cost Comparison**

### **Compute Engine Options:**
```
e2-micro:     ~$6-8/month    (Development)
e2-small:     ~$12-15/month  (Small workloads)
e2-medium:    ~$24-30/month  (Recommended)
e2-standard-2: ~$48-60/month (Medium workloads)
c2-standard-4: ~$120-150/month (High performance)
```

### **GKE Options:**
```
1 node e2-medium:  ~$30/month
2 nodes e2-medium: ~$60/month
1 node e2-standard-2: ~$60/month
```

### **Cloud Run (Serverless):**
```
4GB memory, 2 vCPU: ~$40-80/month (pay per request)
```

---

## 🎯 **Final GCP Recommendation**

### **For Your Use Case:**
```
Recommended Setup:
- Service: Compute Engine
- Machine Type: e2-medium
- vCPU: 2
- Memory: 4GB
- Storage: 20GB Standard Persistent Disk
- Region: us-central1
- Estimated Cost: ~$25-30/month

Why This Works:
✅ Sufficient memory for ML models
✅ Good CPU performance for inference
✅ Cost-effective compared to AWS
✅ Easy to scale up when needed
✅ High reliability with GCP SLA
```

### **Migration Path:**
```
e2-medium → e2-standard-2 → c2-standard-4 → GKE
$30/month → $60/month → $150/month → $200+/month
```

---

## 🔒 **GCP Security Best Practices**

### **1. IAM Configuration**
```bash
# Create service account
gcloud iam service-accounts create qdrant-search-sa \
  --display-name="Qdrant Search Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:qdrant-search-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/compute.viewer"
```

### **2. VPC Configuration**
```bash
# Create custom VPC
gcloud compute networks create qdrant-vpc \
  --subnet-mode=auto

# Create firewall rules
gcloud compute firewall-rules create allow-internal \
  --network=qdrant-vpc \
  --allow tcp,udp,icmp \
  --source-ranges=10.0.0.0/8
```

### **3. SSL/TLS with Load Balancer**
```bash
# Create HTTPS load balancer
gcloud compute ssl-certificates create qdrant-ssl-cert \
  --domains=your-domain.com

gcloud compute backend-services create qdrant-backend \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --protocol=HTTPS
```

---

## 📊 **Performance Monitoring**

### **1. Cloud Monitoring**
```bash
# Enable monitoring
gcloud compute instances add-metadata qdrant-search-app \
  --metadata=enable-oslogin=TRUE

# View metrics in Cloud Console
# - CPU utilization
# - Memory usage
# - Network traffic
# - Disk I/O
```

### **2. Logging**
```bash
# View application logs
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_name=qdrant-search-app"
```

---

## 🚀 **Scaling Strategies**

### **1. Vertical Scaling**
```bash
# Stop instance
gcloud compute instances stop qdrant-search-app --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type qdrant-search-app \
  --machine-type=e2-standard-2 \
  --zone=us-central1-a

# Start instance
gcloud compute instances start qdrant-search-app --zone=us-central1-a
```

### **2. Horizontal Scaling with GKE**
```bash
# Create GKE cluster
gcloud container clusters create qdrant-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium

# Deploy application
kubectl apply -f k8s-deployment.yaml
```

---

## 📝 **GCP Deployment Checklist**

- [ ] GCP project created and billing enabled
- [ ] Compute Engine API enabled
- [ ] Instance created with correct machine type
- [ ] Firewall rules configured
- [ ] Docker and Docker Compose installed
- [ ] Application deployed and tested
- [ ] SSL certificate configured (if using domain)
- [ ] Monitoring and logging enabled
- [ ] Backup strategy implemented
- [ ] Security best practices applied

---

## 🆘 **GCP Troubleshooting**

### **Common Issues:**
1. **Instance not starting**: Check startup script logs
2. **Port not accessible**: Verify firewall rules
3. **High costs**: Monitor usage and optimize
4. **Performance issues**: Upgrade machine type

### **Useful Commands:**
```bash
# Check instance status
gcloud compute instances describe qdrant-search-app --zone=us-central1-a

# View startup script logs
gcloud compute instances get-serial-port-output qdrant-search-app --zone=us-central1-a

# SSH into instance
gcloud compute ssh qdrant-search-app --zone=us-central1-a

# Stop/start instance
gcloud compute instances stop qdrant-search-app --zone=us-central1-a
gcloud compute instances start qdrant-search-app --zone=us-central1-a
```

---

## 🎯 **GCP vs AWS Comparison**

| Feature | GCP (e2-medium) | AWS (t3.medium) |
|---------|-----------------|-----------------|
| **Cost** | ~$25-30/month | ~$35-40/month |
| **vCPU** | 2 | 2 |
| **Memory** | 4GB | 4GB |
| **Performance** | Consistent | Burst |
| **Reliability** | 99.95% SLA | 99.95% SLA |
| **Ease of Use** | Excellent | Good |

**Winner**: GCP is slightly cheaper and offers more consistent performance! 