# CodeRoad AWS Deployment - Step by Step Guide

## 🎯 Overview
This guide will walk you through deploying CodeRoad to AWS for the AI for Bharat hackathon.

**Budget**: $200 ($100 free + $100 credits)  
**Domain**: coderoad.online (Hostinger)  
**Deadline**: March 6, 2026  
**Estimated Time**: 4-6 hours

---

## ✅ Phase 1: Prepare Application (COMPLETED)

### Files Created:
- ✅ `backend/requirements-prod.txt` - Production dependencies
- ✅ `backend/Dockerfile` - Docker image for backend
- ✅ `backend/docker-compose.prod.yml` - Docker Compose for production
- ✅ `backend/.env.production` - Production environment template
- ✅ `frontend/.env.production` - Frontend production config
- ✅ `deploy.sh` - Automated deployment script
- ✅ Updated CORS in `backend/app/config.py`

### What You Need to Know:
1. **Database**: Your app is already PostgreSQL-ready! The code supports both SQLite (dev) and PostgreSQL (production) automatically.
2. **No Code Changes Needed**: Just change the DATABASE_URL environment variable.
3. **Groq API Keys**: All 5 keys are configured and will work from AWS (they're just HTTP API calls).

---

## 🚀 Phase 2: AWS Setup (YOU START HERE)

### Step 1: Create AWS Account & Login
1. Go to https://aws.amazon.com
2. Sign in to your AWS account
3. Verify you have $200 in credits

### Step 2: Launch EC2 Instance

**Why EC2?** It's the simplest and most cost-effective option for your MVP. You can scale later.

#### 2.1 Navigate to EC2
1. In AWS Console, search for "EC2" in the top search bar
2. Click "EC2" to open the EC2 Dashboard
3. Click the orange "Launch Instance" button

#### 2.2 Configure Instance
Fill in these settings:

**Name and tags:**
- Name: `coderoad-backend`

**Application and OS Images (Amazon Machine Image):**
- Quick Start: Ubuntu
- Select: Ubuntu Server 22.04 LTS (Free tier eligible)
- Architecture: 64-bit (x86)

**Instance type:**
- Select: `t3.small` (2 vCPU, 2 GB RAM)
- Cost: ~$15/month
- Why not t2.micro? You need more RAM for PostgreSQL + Backend

**Key pair (login):**
- Click "Create new key pair"
- Key pair name: `coderoad-key`
- Key pair type: RSA
- Private key file format: `.pem` (for Mac/Linux) or `.ppk` (for Windows PuTTY)
- Click "Create key pair"
- **IMPORTANT**: Save this file! You'll need it to SSH into your server

**Network settings:**
- Click "Edit"
- Auto-assign public IP: Enable
- Firewall (security groups): Create security group
- Security group name: `coderoad-sg`
- Description: `Security group for CodeRoad`

Add these rules:
1. SSH (port 22) - Source: My IP (for security)
2. HTTP (port 80) - Source: Anywhere (0.0.0.0/0)
3. HTTPS (port 443) - Source: Anywhere (0.0.0.0/0)
4. Custom TCP (port 8000) - Source: Anywhere (0.0.0.0/0) - for backend API

**Configure storage:**
- Size: 20 GB
- Volume type: gp3 (General Purpose SSD)

**Advanced details:**
- Leave as default

#### 2.3 Launch Instance
1. Review your settings
2. Click "Launch instance"
3. Wait 2-3 minutes for instance to start
4. Click "View all instances"
5. Wait until "Instance state" shows "Running"
6. Note down the "Public IPv4 address" (e.g., 3.123.45.67)

**STOP HERE** - Tell me when you've completed this step and provide:
- Your EC2 public IP address
- Confirmation that you downloaded the .pem key file

---

## 📋 Phase 3: Deploy Backend (NEXT)

### Step 3: Connect to EC2 Instance

**For Windows (using Git Bash or WSL):**
```bash
# Navigate to where you saved the key
cd ~/Downloads

# Set permissions
chmod 400 coderoad-key.pem

# Connect to EC2
ssh -i coderoad-key.pem ubuntu@YOUR_EC2_IP
```

**For Windows (using PuTTY):**
1. Open PuTTY
2. Host Name: ubuntu@YOUR_EC2_IP
3. Connection > SSH > Auth > Browse for your .ppk file
4. Click "Open"

### Step 4: Run Deployment Script

Once connected to EC2, run these commands:

```bash
# Download deployment script
curl -o deploy.sh https://raw.githubusercontent.com/sanyamChaudhary27/CodeRoad/feature/aws-deployment/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
- Install all dependencies (Python, Docker, Nginx)
- Clone your repository
- Setup PostgreSQL in Docker
- Start the backend service
- Configure Nginx reverse proxy

**STOP HERE** - Tell me when the script completes and share any errors if it fails.

---

## 🌐 Phase 4: Configure Domain (NEXT)

### Step 5: Point Domain to EC2

You need to update DNS records on Hostinger:

1. Login to Hostinger
2. Go to "Domains" > "coderoad.online" > "DNS Zone"
3. Add/Update these records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_EC2_IP | 3600 |
| A | www | YOUR_EC2_IP | 3600 |

4. Save changes
5. Wait 5-10 minutes for DNS propagation

**Test DNS:**
```bash
# On your local machine
ping coderoad.online
# Should show your EC2 IP
```

### Step 6: Setup SSL Certificate

Once DNS is working, SSH back into EC2 and run:

```bash
sudo certbot --nginx -d coderoad.online -d www.coderoad.online
```

Follow the prompts:
- Enter your email
- Agree to terms
- Choose option 2 (Redirect HTTP to HTTPS)

**STOP HERE** - Tell me when SSL is setup and you can access https://coderoad.online

---

## 🎨 Phase 5: Deploy Frontend (NEXT)

### Step 7: Build Frontend

On your local machine:

```bash
cd frontend

# Install dependencies (if not already)
npm install

# Build for production
npm run build
```

This creates a `dist/` folder with optimized files.

### Step 8: Create S3 Bucket

```bash
# Install AWS CLI if not already installed
# Windows: Download from https://aws.amazon.com/cli/
# Mac: brew install awscli
# Linux: sudo apt install awscli

# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json

# Create S3 bucket
aws s3 mb s3://coderoad-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://coderoad-frontend --index-document index.html --error-document index.html

# Upload files
cd frontend
aws s3 sync dist/ s3://coderoad-frontend --delete

# Make bucket public
aws s3api put-bucket-policy --bucket coderoad-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::coderoad-frontend/*"
  }]
}'
```

### Step 9: Setup CloudFront (Optional but Recommended)

CloudFront provides:
- Global CDN (faster loading worldwide)
- Free SSL certificate
- Better performance

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name coderoad-frontend.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html
```

Note the CloudFront domain (e.g., d1234567890.cloudfront.net)

**STOP HERE** - Tell me when frontend is deployed and share the S3/CloudFront URL

---

## 🧪 Phase 6: Testing (FINAL)

### Step 10: Test Everything

1. **Frontend**: Visit https://coderoad.online
2. **Backend Health**: Visit https://coderoad.online/api/health
3. **Register**: Create a new account
4. **Login**: Login with your account
5. **Dashboard**: Check if dashboard loads
6. **Arena**: Start a match and test gameplay
7. **Leaderboard**: Check if leaderboard displays
8. **Profile**: View your profile

### Step 11: Monitor Logs

```bash
# SSH into EC2
ssh -i coderoad-key.pem ubuntu@YOUR_EC2_IP

# View backend logs
sudo journalctl -u coderoad -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View PostgreSQL logs
docker logs -f coderoad-postgres
```

---

## 💰 Cost Breakdown

| Service | Specs | Monthly Cost |
|---------|-------|--------------|
| EC2 t3.small | 2 vCPU, 2GB RAM | $15 |
| S3 + CloudFront | Static hosting | $5-10 |
| Data Transfer | Estimated | $5 |
| **Total** | | **$25-30/month** |

**Your Budget**: $200 = 6-8 months of hosting ✅

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check service status
sudo systemctl status coderoad

# View logs
sudo journalctl -u coderoad -n 100

# Restart service
sudo systemctl restart coderoad
```

### Database connection error
```bash
# Check PostgreSQL
docker ps | grep postgres

# View PostgreSQL logs
docker logs coderoad-postgres

# Restart PostgreSQL
docker restart coderoad-postgres
```

### Frontend shows CORS error
1. Check backend CORS settings in `backend/app/config.py`
2. Verify frontend API URL in `frontend/.env.production`
3. Rebuild and redeploy frontend

### SSL certificate issues
```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## 📝 Important Notes

### Database Migration (SQLite → PostgreSQL)
**Good news**: No code changes needed! Your app already supports PostgreSQL.

Just update the DATABASE_URL:
```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./coderoad.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://coderoad:password@localhost:5432/coderoad
```

The `backend/app/core/database.py` automatically detects the database type and configures accordingly.

### Environment Variables
**NEVER commit these to git:**
- SECRET_KEY
- Database passwords
- API keys

Always use `.env.production` file on the server.

### Backup Strategy
```bash
# Backup PostgreSQL
docker exec coderoad-postgres pg_dump -U coderoad coderoad > backup.sql

# Restore PostgreSQL
docker exec -i coderoad-postgres psql -U coderoad coderoad < backup.sql
```

---

## 🎉 Success Checklist

- [ ] EC2 instance running
- [ ] Backend service active
- [ ] PostgreSQL running
- [ ] Domain pointing to EC2
- [ ] SSL certificate installed
- [ ] Frontend deployed to S3
- [ ] CloudFront distribution created
- [ ] Can register new user
- [ ] Can login
- [ ] Can start match
- [ ] Leaderboard works
- [ ] Profile page loads

---

## 🆘 Need Help?

If you get stuck at any step:
1. Share the exact error message
2. Share relevant logs
3. Share which step you're on
4. I'll help you debug!

---

## 🚀 Ready to Deploy?

Start with **Phase 2, Step 1** above. Take it one step at a time, and stop at each "STOP HERE" point to confirm everything is working before moving forward.

Good luck! 🎯
