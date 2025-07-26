# AWS Deployment Guide - Qdrant Search Application

## 🎯 **Recommended Setup: EC2 t3.small with Docker**

### **Estimated Costs:**
- **EC2 t3.small**: ~$16-20/month
- **EBS Storage (20GB)**: ~$2/month
- **Data Transfer**: ~$1-5/month
- **Total**: ~$20-30/month

---

## 📋 **Step-by-Step Deployment**

### **Step 1: Launch EC2 Instance**

#### **Instance Configuration:**
- **Instance Type**: t3.small (2 vCPU, 2GB RAM)
- **AMI**: Amazon Linux 2023
- **Storage**: 20GB GP3 EBS
- **Security Group**: Custom (see below)

#### **Security Group Rules:**
```
Inbound Rules:
- SSH (22): Your IP only
- HTTP (80): 0.0.0.0/0 (optional, for web access)
- Custom TCP (8000): 0.0.0.0/0 (API access)
- Custom TCP (5433): 0.0.0.0/0 (Database access, if needed)
- Custom TCP (6333): 0.0.0.0/0 (Qdrant access, if needed)

Outbound Rules:
- All traffic: 0.0.0.0/0
```

### **Step 2: Connect and Setup Server**

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-public-ip

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install -y git

# Logout and login again for docker group to take effect
exit
# SSH back in
```

### **Step 3: Clone and Deploy Application**

```bash
# Clone your repository
git clone https://github.com/yourusername/faissGrocerEase.git
cd faissGrocerEase

# Create production docker-compose file
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your_secure_password_here
      - POSTGRES_DB=grocerease
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - db
      - qdrant
    restart: unless-stopped

  db:
    image: postgis/postgis:15-3.3
    ports:
      - "5433:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your_secure_password_here
      - POSTGRES_DB=grocerease
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  postgres_data:
  qdrant_data:
EOF

# Start services
docker-compose -f docker-compose.prod.yml up -d db qdrant

# Wait for databases to be ready
sleep 30

# Start app
docker-compose -f docker-compose.prod.yml up -d app

# Ingest data
docker-compose -f docker-compose.prod.yml exec app python -m scripts.ingest_products_qdrant
```

### **Step 4: Test Deployment**

```bash
# Test API
curl -X GET "http://localhost:8000/"

# Test search
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "electronics", "lat": 0.0, "lon": 0.0, "radius_km": 10000.0, "max_results": 3}'
```

### **Step 5: Configure for External Access**

#### **Option A: Direct Port Access (Simple)**
```bash
# Your API will be available at:
# http://your-ec2-public-ip:8000
# http://your-ec2-public-ip:8000/docs
```

#### **Option B: Nginx Reverse Proxy (Recommended)**
```bash
# Install Nginx
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Create Nginx config
sudo tee /etc/nginx/conf.d/api.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 public IP

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 **Production Optimizations**

### **1. Environment Variables**
```bash
# Create .env file
cat > .env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_very_secure_password_here
POSTGRES_DB=grocerease
POSTGRES_HOST=db
POSTGRES_PORT=5432
QDRANT_URL=http://qdrant:6333
EOF
```

### **2. Docker Production Optimizations**
```dockerfile
# Add to your Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **3. Monitoring and Logging**
```bash
# Install monitoring tools
sudo yum install -y htop iotop

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

---

## 💰 **Cost Optimization Tips**

### **1. Instance Sizing**
- **Development**: t3.micro (Free tier)
- **Small Production**: t3.small
- **Medium Production**: t3.medium
- **High Traffic**: t3.large or c5.large

### **2. Storage Optimization**
- Use GP3 EBS volumes (cheaper than GP2)
- Start with 20GB, scale as needed
- Consider EBS snapshots for backups

### **3. Network Optimization**
- Use CloudFront for static content (if any)
- Consider API Gateway for advanced features
- Monitor data transfer costs

---

## 🔒 **Security Considerations**

### **1. Firewall Rules**
```bash
# Only allow necessary ports
# Remove port 5433 from public access if not needed
# Use VPC security groups for internal communication
```

### **2. SSL/TLS**
```bash
# Install Certbot for Let's Encrypt SSL
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### **3. Database Security**
```bash
# Use strong passwords
# Consider RDS for production databases
# Enable encryption at rest
```

---

## 📊 **Performance Monitoring**

### **1. Basic Monitoring**
```bash
# Check resource usage
htop
df -h
docker stats

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/"
```

### **2. CloudWatch Integration**
```bash
# Install CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent
# Configure monitoring
```

---

## 🚀 **Scaling Options**

### **1. Vertical Scaling**
- Upgrade to larger instance types
- Increase EBS volume size

### **2. Horizontal Scaling**
- Use Application Load Balancer
- Deploy multiple EC2 instances
- Consider ECS/EKS for container orchestration

### **3. Database Scaling**
- Migrate to RDS for managed database
- Use read replicas for read-heavy workloads
- Consider Aurora for high performance

---

## 📝 **Deployment Checklist**

- [ ] EC2 instance launched with correct security groups
- [ ] Docker and Docker Compose installed
- [ ] Application cloned and configured
- [ ] Environment variables set
- [ ] Services started and healthy
- [ ] Data ingested successfully
- [ ] API endpoints tested
- [ ] External access configured
- [ ] SSL certificate installed (if using domain)
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented

---

## 🆘 **Troubleshooting**

### **Common Issues:**
1. **Port not accessible**: Check security groups
2. **Database connection fails**: Verify environment variables
3. **Memory issues**: Upgrade instance type
4. **Disk space**: Increase EBS volume size

### **Useful Commands:**
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs app

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres grocerease > backup.sql
``` 