# Code Road - AWS Deployment Guide

## Deployment Timeline: March 2-6, 2026

This guide provides step-by-step instructions for deploying Code Road to AWS by March 6, 2026.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CloudFront (CDN)                                 │  │
│  │  - Frontend static files                          │  │
│  │  - Global distribution                            │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                      │
│  ┌────────────────▼─────────────────────────────────┐  │
│  │  S3 Bucket                                        │  │
│  │  - React build files                              │  │
│  │  - Static assets                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Application Load Balancer                        │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                      │
│  ┌────────────────▼─────────────────────────────────┐  │
│  │  ECS Fargate (Backend)                            │  │
│  │  - FastAPI application                            │  │
│  │  - Auto-scaling enabled                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RDS (PostgreSQL) or SQLite on EFS                │  │
│  │  - Database                                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ElastiCache (Redis) - Optional                   │  │
│  │  - Caching layer                                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Important Technical Clarifications

### Why PostgreSQL Instead of SQLite?

**SQLite Limitations:**
- ❌ No concurrent write support (only one write at a time)
- ❌ File-based (can't share between containers)
- ❌ Not suitable for WebSocket connections with multiple users
- ❌ Locking issues under load
- ❌ No network access

**PostgreSQL Benefits:**
- ✅ Handles concurrent connections (essential for WebSockets)
- ✅ Network-based (multiple containers can connect)
- ✅ ACID transactions
- ✅ Production-ready
- ✅ Scales with your application

**WebSocket + Database:**
When users connect via WebSocket:
1. User A connects → writes to database
2. User B connects → writes to database (simultaneously)
3. SQLite would lock/fail, PostgreSQL handles it properly

### Gemini API from AWS

**Yes, it works perfectly!**

The Gemini API is just a REST API that your backend calls:
```
Your Backend (AWS) → HTTPS → Google Gemini API
```

**How it works:**
1. Your FastAPI backend makes HTTP requests to `generativelanguage.googleapis.com`
2. Sends your API key in the request
3. Receives generated content back
4. No special AWS configuration needed

**Security:**
- API key is stored in environment variables
- Transmitted over HTTPS
- Works from any cloud provider (AWS, GCP, Azure)
- No firewall issues (outbound HTTPS is allowed by default)

**Testing:**
Run the test script to verify:
```bash
python test_gemini_api.py
```

### Database Options Comparison

| Feature | SQLite | PostgreSQL (RDS) | PostgreSQL (Docker) |
|---------|--------|------------------|---------------------|
| Cost | Free | ~$15/month | Free |
| Concurrent Users | ❌ Limited | ✅ Unlimited | ✅ Unlimited |
| WebSocket Support | ❌ Poor | ✅ Excellent | ✅ Excellent |
| Backups | Manual | ✅ Automatic | Manual |
| Scaling | ❌ No | ✅ Yes | Limited |
| Setup Complexity | Easy | Medium | Easy |
| **Recommendation** | Dev only | Production | MVP/Small scale |

### Recommended Deployment Strategy

**For MVP (March 6 deadline):**
1. Use EC2 with PostgreSQL in Docker
2. Simple, fast setup
3. Handles WebSockets properly
4. Can migrate to RDS later

**For Production (after launch):**
1. Migrate to RDS PostgreSQL
2. Add Redis for caching
3. Use ECS Fargate for auto-scaling
4. Add CloudFront CDN

---

## Prerequisites

- AWS Account with billing enabled
- AWS CLI installed and configured
- Docker installed locally
- Node.js 18+ installed
- Python 3.11+ installed

---

## Phase 1: Frontend Deployment (Day 1 - March 2)

### Step 1: Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with optimized production files.

### Step 2: Create S3 Bucket

```bash
# Create bucket (replace with your bucket name)
aws s3 mb s3://coderoad-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://coderoad-frontend --index-document index.html --error-document index.html

# Upload build files
aws s3 sync dist/ s3://coderoad-frontend --delete
```

### Step 3: Configure S3 Bucket Policy

Create `s3-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::coderoad-frontend/*"
    }
  ]
}
```

Apply policy:

```bash
aws s3api put-bucket-policy --bucket coderoad-frontend --policy file://s3-policy.json
```

### Step 4: Setup CloudFront (Optional but Recommended)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name coderoad-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

Note the CloudFront domain name (e.g., `d1234567890.cloudfront.net`)

---

## Phase 2: Backend Deployment (Day 2-3 - March 3-4)

### Option A: Deploy to ECS Fargate (Recommended)

#### Step 1: Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name coderoad-backend --region us-east-1

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### Step 2: Build and Push Docker Image

```bash
cd backend

# Build image
docker build -t coderoad-backend .

# Tag image
docker tag coderoad-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/coderoad-backend:latest

# Push to ECR
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/coderoad-backend:latest
```

#### Step 3: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name coderoad-cluster --region us-east-1
```

#### Step 4: Setup RDS PostgreSQL Database (Recommended for Production)

**Why PostgreSQL instead of SQLite?**
- SQLite doesn't support concurrent writes (bad for WebSockets)
- No network access (can't share between containers)
- Not suitable for production with multiple users
- PostgreSQL handles concurrent connections properly

Create RDS instance:

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name coderoad-db-subnet \
  --db-subnet-group-description "CodeRoad DB Subnet" \
  --subnet-ids subnet-xxx subnet-yyy

# Create security group for RDS
aws ec2 create-security-group \
  --group-name coderoad-rds-sg \
  --description "Security group for CodeRoad RDS" \
  --vpc-id <your-vpc-id>

# Allow PostgreSQL from backend security group
aws ec2 authorize-security-group-ingress \
  --group-id <rds-sg-id> \
  --protocol tcp \
  --port 5432 \
  --source-group <backend-sg-id>

# Create RDS PostgreSQL instance (db.t3.micro for low cost)
aws rds create-db-instance \
  --db-instance-identifier coderoad-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username coderoad \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids <rds-sg-id> \
  --db-subnet-group-name coderoad-db-subnet \
  --backup-retention-period 7 \
  --no-publicly-accessible

# Wait for DB to be available (takes 5-10 minutes)
aws rds wait db-instance-available --db-instance-identifier coderoad-db

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier coderoad-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

**Alternative: Use SQLite for MVP (Not Recommended)**
If you want to start simple and migrate later, you can use SQLite with EFS:
- Mount EFS volume to container
- Store SQLite file on EFS
- Note: Still has concurrency limitations

#### Step 5: Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "coderoad-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "coderoad-backend",
      "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/coderoad-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SECRET_KEY",
          "value": "your-production-secret-key-change-this"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://coderoad:YOUR_SECURE_PASSWORD@your-rds-endpoint:5432/postgres"
        },
        {
          "name": "AI_PROVIDER",
          "value": "gemini"
        },
        {
          "name": "GEMINI_API_KEY",
          "value": "AIzaSyAYeSMWtjcn3JrF3bbmCI6Wqq5Dn4KabiE"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/coderoad-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Important Notes:**
- Replace `YOUR_SECURE_PASSWORD` with your actual RDS password
- Replace `your-rds-endpoint` with the RDS endpoint from previous step
- The Gemini API key works fine from AWS (it's just an HTTP API call)
- For better security, use AWS Secrets Manager instead of hardcoding values

Register task:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Step 5: Create Application Load Balancer

```bash
# Create security group for ALB
aws ec2 create-security-group \
  --group-name coderoad-alb-sg \
  --description "Security group for CodeRoad ALB" \
  --vpc-id <your-vpc-id>

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Create ALB
aws elbv2 create-load-balancer \
  --name coderoad-alb \
  --subnets <subnet-1> <subnet-2> \
  --security-groups <sg-id>
```

#### Step 6: Create ECS Service

```bash
aws ecs create-service \
  --cluster coderoad-cluster \
  --service-name coderoad-backend-service \
  --task-definition coderoad-backend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-1>,<subnet-2>],securityGroups=[<sg-id>],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=<target-group-arn>,containerName=coderoad-backend,containerPort=8000"
```

### Option B: Deploy to EC2 (Simpler, Lower Cost)

**Recommended for MVP**: This is simpler and you can use PostgreSQL in Docker or install it locally.

#### Step 1: Launch EC2 Instance

```bash
# Launch t3.small instance with Ubuntu 22.04
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --security-group-ids <sg-id> \
  --subnet-id <subnet-id> \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=coderoad-backend}]'
```

#### Step 2: SSH and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<instance-public-ip>

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip git docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker ubuntu
newgrp docker

# Clone repository
git clone https://github.com/sanyamChaudhary27/CodeRoad.git
cd CodeRoad

# Start PostgreSQL with Docker
docker run -d \
  --name postgres \
  -e POSTGRES_DB=coderoad \
  -e POSTGRES_USER=coderoad \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Wait for PostgreSQL to start
sleep 10

# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=your-production-secret-key-change-this
DATABASE_URL=postgresql://coderoad:your_secure_password@localhost:5432/coderoad
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAYeSMWtjcn3JrF3bbmCI6Wqq5Dn4KabiE
EOF

# Test backend
python3 -m uvicorn app.app:app --host 0.0.0.0 --port 8000
# Press Ctrl+C after verifying it starts

# Run with systemd
sudo nano /etc/systemd/system/coderoad.service
```

Create service file:

```ini
[Unit]
Description=CodeRoad Backend
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/CodeRoad/backend
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable coderoad
sudo systemctl start coderoad
sudo systemctl status coderoad

# Check logs
sudo journalctl -u coderoad -f
```

**WebSocket Support:**
- PostgreSQL handles concurrent connections properly
- FastAPI's WebSocket implementation works with PostgreSQL
- Multiple users can connect simultaneously
- Database transactions are ACID compliant

---

## Phase 3: Configure CORS and Environment (Day 4 - March 5)

### Update Backend CORS

Edit `backend/app/config.py`:

```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://d1234567890.cloudfront.net",  # Your CloudFront domain
    "https://coderoad-frontend.s3.amazonaws.com",  # Your S3 domain
    "https://your-custom-domain.com"  # If using custom domain
]
```

### Update Frontend API URL

Edit `frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://your-alb-domain.us-east-1.elb.amazonaws.com'  // Or EC2 public IP
  : 'http://localhost:8000';
```

Rebuild and redeploy frontend:

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://coderoad-frontend --delete
```

---

## Phase 4: Testing and Monitoring (Day 5 - March 6)

### Test Deployment

1. **Frontend**: Visit CloudFront URL or S3 website URL
2. **Backend Health**: `curl https://your-backend-url/health`
3. **Register User**: Test registration flow
4. **Login**: Test authentication
5. **Start Match**: Test matchmaking and arena

### Setup CloudWatch Monitoring

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/coderoad-backend

# Create alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name coderoad-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## Cost Estimation

### Monthly Costs (Approximate)

**Option 1: EC2 + Docker PostgreSQL (Recommended for MVP)**
- S3 + CloudFront: $5-10/month
- EC2 t3.small: $15/month
- Data transfer: $5/month
- **Total: $25-35/month**

**Option 2: ECS Fargate + RDS**
- S3 + CloudFront: $5-10/month
- ECS Fargate (1 task): $15-20/month
- RDS db.t3.micro: $15/month
- Data transfer: $5/month
- **Total: $40-50/month**

**Option 3: Full Production Setup**
- S3 + CloudFront: $10/month
- ECS Fargate (2 tasks): $30-40/month
- RDS db.t3.small: $30/month
- ElastiCache Redis: $15/month
- Data transfer: $10/month
- **Total: $95-105/month**

### Cost Optimization

- Start with Option 1 (EC2 + Docker PostgreSQL)
- Migrate to Option 2 when you have 100+ daily users
- Upgrade to Option 3 when you have 1000+ daily users
- Use Reserved Instances for 30-40% savings
- Enable S3 lifecycle policies
- Use CloudFront caching aggressively

---

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS for all endpoints
- [ ] Enable AWS WAF on ALB
- [ ] Restrict security group rules
- [ ] Enable CloudTrail logging
- [ ] Use AWS Secrets Manager for API keys
- [ ] Enable S3 bucket encryption
- [ ] Setup IAM roles with least privilege

---

## Rollback Plan

If deployment fails:

1. **Frontend**: Previous S3 version available via versioning
2. **Backend**: Rollback ECS task definition to previous version
3. **Database**: Restore from RDS snapshot (if using RDS)

```bash
# Rollback ECS service
aws ecs update-service \
  --cluster coderoad-cluster \
  --service coderoad-backend-service \
  --task-definition coderoad-backend:1  # Previous version
```

---

## Custom Domain Setup (Optional)

### Step 1: Register Domain (Route 53)

```bash
aws route53 create-hosted-zone --name coderoad.com --caller-reference $(date +%s)
```

### Step 2: Create SSL Certificate (ACM)

```bash
aws acm request-certificate \
  --domain-name coderoad.com \
  --subject-alternative-names www.coderoad.com \
  --validation-method DNS
```

### Step 3: Update CloudFront with Custom Domain

Update CloudFront distribution to use custom domain and SSL certificate.

---

## Troubleshooting

### Frontend Issues

- **Blank page**: Check browser console for CORS errors
- **API errors**: Verify API_BASE_URL is correct
- **404 on refresh**: Ensure CloudFront has error page redirect to index.html

### Backend Issues

- **Container won't start**: Check CloudWatch logs
- **Database errors**: Verify DATABASE_URL is correct
- **API key errors**: Check GEMINI_API_KEY is set

### Common Commands

```bash
# View ECS logs
aws logs tail /ecs/coderoad-backend --follow

# Check ECS service status
aws ecs describe-services --cluster coderoad-cluster --services coderoad-backend-service

# Update ECS service
aws ecs update-service --cluster coderoad-cluster --service coderoad-backend-service --force-new-deployment
```

---

## Post-Deployment Checklist

- [ ] Frontend accessible via CloudFront/S3
- [ ] Backend health check returns 200
- [ ] User registration works
- [ ] User login works
- [ ] Matchmaking works
- [ ] Arena loads correctly
- [ ] Profile page accessible
- [ ] Leaderboard displays
- [ ] CloudWatch monitoring enabled
- [ ] Backup strategy in place
- [ ] Documentation updated

---

## Support and Maintenance

### Daily Tasks
- Monitor CloudWatch logs
- Check error rates
- Review user feedback

### Weekly Tasks
- Review AWS costs
- Update dependencies
- Backup database

### Monthly Tasks
- Security audit
- Performance optimization
- Feature updates

---

## Conclusion

This deployment guide provides a complete path to AWS deployment by March 6, 2026. The application is fully compatible with AWS services and can be deployed using either ECS Fargate (scalable) or EC2 (cost-effective).

**Recommended Approach**: Start with EC2 for simplicity, then migrate to ECS Fargate as traffic grows.

**Status**: ✅ Ready for AWS Deployment
**Timeline**: March 2-6, 2026
**Estimated Setup Time**: 4-6 hours
