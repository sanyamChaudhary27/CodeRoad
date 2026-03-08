# 🚀 CodeRoad AWS Deployment - Quick Start

## 📋 What You Need

- ✅ AWS Account with $200 credits
- ✅ Domain: coderoad.online (Hostinger)
- ✅ 2-3 hours of time
- ✅ This codebase (already prepared!)

---

## 🎯 5-Step Deployment

### Step 1: Launch EC2 (15 min)
```
AWS Console → EC2 → Launch Instance
- Name: coderoad-backend
- OS: Ubuntu 22.04
- Type: t3.small
- Security: Allow ports 22, 80, 443, 8000
- Download .pem key file
```

**STOP** → Note your EC2 public IP

---

### Step 2: Deploy Backend (30 min)
```bash
# SSH into EC2
ssh -i coderoad-key.pem ubuntu@YOUR_EC2_IP

# Download and run deployment script
curl -o deploy.sh https://raw.githubusercontent.com/sanyamChaudhary27/CodeRoad/feature/aws-deployment/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

**STOP** → Verify backend is running: `curl http://localhost:8000/health`

---

### Step 3: Configure Domain (20 min)
```
Hostinger → Domains → coderoad.online → DNS Zone
Add A records:
- @ → YOUR_EC2_IP
- www → YOUR_EC2_IP

Wait 5-10 minutes for DNS propagation
```

**Test**: `ping coderoad.online` should show your EC2 IP

```bash
# Setup SSL
ssh -i coderoad-key.pem ubuntu@YOUR_EC2_IP
sudo certbot --nginx -d coderoad.online -d www.coderoad.online
```

**STOP** → Visit https://coderoad.online/api/health

---

### Step 4: Deploy Frontend (20 min)
```bash
# On your local machine
cd frontend
npm install
npm run build

# Install AWS CLI (if not installed)
# Windows: https://aws.amazon.com/cli/
# Mac: brew install awscli

# Configure AWS
aws configure
# Enter your Access Key ID and Secret Key

# Create S3 bucket and upload
aws s3 mb s3://coderoad-frontend --region us-east-1
aws s3 website s3://coderoad-frontend --index-document index.html
aws s3 sync dist/ s3://coderoad-frontend --delete

# Make public
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

**STOP** → Visit http://coderoad-frontend.s3-website-us-east-1.amazonaws.com

---

### Step 5: Test Everything (15 min)
- [ ] Visit https://coderoad.online
- [ ] Register new account
- [ ] Login
- [ ] View Dashboard
- [ ] Start a match in Arena
- [ ] Check Leaderboard
- [ ] View Profile

---

## 🆘 Quick Troubleshooting

### Backend not starting?
```bash
ssh -i coderoad-key.pem ubuntu@YOUR_EC2_IP
sudo systemctl status coderoad
sudo journalctl -u coderoad -n 50
```

### Database error?
```bash
docker ps | grep postgres
docker logs coderoad-postgres
docker restart coderoad-postgres
```

### Frontend CORS error?
Check browser console. Backend CORS is already configured for coderoad.online.

### SSL not working?
```bash
sudo certbot renew
sudo systemctl restart nginx
```

---

## 💰 Monthly Cost: $25-30

- EC2 t3.small: $15
- S3 + CloudFront: $5-10
- Data Transfer: $5

Your $200 = 6-8 months ✅

---

## 📚 Full Documentation

- **Detailed Guide**: `DEPLOYMENT_STEPS.md`
- **Phase 1 Summary**: `PHASE_1_COMPLETE.md`
- **AWS Architecture**: `AWS_DEPLOYMENT_GUIDE.md`

---

## ✅ You're Ready!

Everything is prepared. Just follow the 5 steps above.

**Start with Step 1** → Launch EC2 Instance

Good luck! 🎯
