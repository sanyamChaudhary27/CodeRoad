# Code Road - Quick Deploy Guide (MVP)

## Goal: Get live on AWS by March 6, 2026

This is the **simplest, fastest** way to deploy. Takes ~4-6 hours total.

---

## Architecture (Simple)

```
┌─────────────────────────────────────────┐
│  CloudFront/S3 (Frontend)               │
│  - React app                            │
└────────────┬────────────────────────────┘
             │
             │ HTTPS
             │
┌────────────▼────────────────────────────┐
│  EC2 Instance (t3.small)                │
│  ┌────────────────────────────────────┐ │
│  │ FastAPI Backend (Port 8000)        │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ PostgreSQL (Docker)                │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Why this setup?**
- ✅ Simple to deploy
- ✅ PostgreSQL handles WebSockets properly
- ✅ Low cost (~$25/month)
- ✅ Can scale later
- ✅ Gemini API works perfectly

---

## Step 1: Test Gemini API (5 minutes)

```bash
# Run the test script
python test_gemini_api.py
```

**Expected output:**
```
✅ ALL TESTS PASSED!
✓ Gemini API key is valid and working
✓ Can generate basic text
✓ Can generate coding problems
🚀 Ready for deployment!
```

If it fails, check:
- API key in `backend/.env` is correct
- You have internet connection
- API key has Gemini API enabled in Google Cloud Console

---

## Step 2: Deploy Frontend to S3 (30 minutes)

### 2.1 Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates `dist/` folder with production files.

### 2.2 Create S3 Bucket

```bash
# Replace 'coderoad-frontend' with your unique bucket name
aws s3 mb s3://coderoad-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://coderoad-frontend \
  --index-document index.html \
  --error-document index.html
```

### 2.3 Upload Files

```bash
# Upload build
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

### 2.4 Get URL

```bash
echo "http://coderoad-frontend.s3-website-us-east-1.amazonaws.com"
```

Test it in browser - you should see the login page (API calls will fail until backend is deployed).

---

## Step 3: Deploy Backend to EC2 (2-3 hours)

### 3.1 Launch EC2 Instance

**Via AWS Console (Easier):**
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose:
   - Name: `coderoad-backend`
   - AMI: Ubuntu Server 22.04 LTS
   - Instance type: t3.small
   - Key pair: Create new or use existing
   - Security group: Create new with rules:
     - SSH (22) from your IP
     - HTTP (80) from anywhere
     - Custom TCP (8000) from anywhere
4. Click "Launch Instance"
5. Wait 2 minutes for it to start

### 3.2 Connect to EC2

```bash
# Get public IP from AWS Console
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 3.3 Setup Backend

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3-pip git docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker ubuntu
newgrp docker

# Clone repository
git clone https://github.com/sanyamChaudhary27/CodeRoad.git
cd CodeRoad

# Start PostgreSQL
docker run -d \
  --name postgres \
  --restart always \
  -e POSTGRES_DB=coderoad \
  -e POSTGRES_USER=coderoad \
  -e POSTGRES_PASSWORD=SecurePassword123 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Wait for PostgreSQL
sleep 15

# Install Python packages
cd backend
pip3 install -r requirements.txt

# Create production .env
cat > .env << 'EOF'
SECRET_KEY=change-this-to-random-string-in-production
DATABASE_URL=postgresql://coderoad:SecurePassword123@localhost:5432/coderoad
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAYeSMWtjcn3JrF3bbmCI6Wqq5Dn4KabiE
EOF

# Test backend
python3 -m uvicorn app.app:app --host 0.0.0.0 --port 8000
```

**Test in browser:** `http://YOUR_EC2_IP:8000/health`

Should return: `{"status":"healthy"}`

Press Ctrl+C to stop.

### 3.4 Setup Auto-Start with Systemd

```bash
# Create service file
sudo tee /etc/systemd/system/coderoad.service > /dev/null << 'EOF'
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
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable coderoad
sudo systemctl start coderoad

# Check status
sudo systemctl status coderoad

# View logs
sudo journalctl -u coderoad -f
```

---

## Step 4: Connect Frontend to Backend (30 minutes)

### 4.1 Update Backend CORS

On EC2:

```bash
cd ~/CodeRoad/backend
nano app/config.py
```

Find `CORS_ORIGINS` and add your S3 URL:

```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://coderoad-frontend.s3-website-us-east-1.amazonaws.com",  # Add this
]
```

Save and restart:

```bash
sudo systemctl restart coderoad
```

### 4.2 Update Frontend API URL

On your local machine:

```bash
cd frontend/src/lib
nano api.ts
```

Update:

```typescript
const API_BASE_URL = import.meta.env.PROD 
  ? 'http://YOUR_EC2_PUBLIC_IP:8000'  // Change this
  : 'http://localhost:8000';
```

### 4.3 Rebuild and Redeploy Frontend

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://coderoad-frontend --delete
```

---

## Step 5: Test Everything (30 minutes)

### 5.1 Open Frontend

Visit: `http://coderoad-frontend.s3-website-us-east-1.amazonaws.com`

### 5.2 Test Flow

1. **Register**: Create new account
2. **Login**: Sign in
3. **Dashboard**: Should load with arena cards
4. **Solo Practice**: Click on DSA Arena → Solo Practice
5. **Arena**: Should load a challenge
6. **Profile**: Navigate to profile page
7. **Leaderboard**: Check leaderboard

### 5.3 Check Backend Logs

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
sudo journalctl -u coderoad -f
```

Look for:
- No errors
- API requests being logged
- Database connections working

---

## Troubleshooting

### Frontend shows blank page
- Check browser console for errors
- Verify CORS is configured correctly
- Check API_BASE_URL is correct

### Backend not responding
```bash
# Check if service is running
sudo systemctl status coderoad

# Check logs
sudo journalctl -u coderoad -n 50

# Check if PostgreSQL is running
docker ps

# Restart everything
sudo systemctl restart coderoad
```

### Database errors
```bash
# Check PostgreSQL logs
docker logs postgres

# Restart PostgreSQL
docker restart postgres

# Recreate database
docker stop postgres
docker rm postgres
# Then run the docker run command again from Step 3.3
```

### Gemini API not working
```bash
# Test API key
cd ~/CodeRoad
python3 test_gemini_api.py

# Check .env file
cat backend/.env | grep GEMINI
```

---

## Post-Deployment Checklist

- [ ] Frontend loads at S3 URL
- [ ] Backend health check returns 200
- [ ] Can register new user
- [ ] Can login
- [ ] Dashboard displays correctly
- [ ] Can start practice match
- [ ] Arena loads challenge
- [ ] Profile page works
- [ ] Leaderboard displays
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## Monitoring

### Check Backend Status

```bash
# Service status
sudo systemctl status coderoad

# Recent logs
sudo journalctl -u coderoad -n 100

# Follow logs live
sudo journalctl -u coderoad -f

# Check resource usage
htop
```

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U coderoad -d coderoad

# List tables
\dt

# Count users
SELECT COUNT(*) FROM players;

# Exit
\q
```

---

## Costs

**Monthly:**
- EC2 t3.small: ~$15
- S3 + Data transfer: ~$5-10
- **Total: ~$20-25/month**

**To reduce costs:**
- Stop EC2 when not in use (dev/testing)
- Use t3.micro instead of t3.small ($7.50/month)
- Enable S3 lifecycle policies

---

## Next Steps (After Launch)

### Week 1
- Monitor error logs daily
- Gather user feedback
- Fix any bugs

### Week 2
- Add CloudFront CDN for faster frontend
- Setup automated backups
- Add monitoring/alerts

### Month 2
- Consider migrating to RDS for better reliability
- Add Redis for caching
- Implement auto-scaling

---

## Upgrade Path

### When you have 100+ users:
1. Add CloudFront CDN
2. Migrate to RDS PostgreSQL
3. Add Redis for caching
4. Setup CloudWatch monitoring

### When you have 1000+ users:
1. Migrate to ECS Fargate
2. Add auto-scaling
3. Use Application Load Balancer
4. Add ElastiCache Redis
5. Setup CI/CD pipeline

---

## Important URLs

**Save these:**
- Frontend: `http://coderoad-frontend.s3-website-us-east-1.amazonaws.com`
- Backend: `http://YOUR_EC2_IP:8000`
- API Docs: `http://YOUR_EC2_IP:8000/docs`
- Health Check: `http://YOUR_EC2_IP:8000/health`

---

## Support

### If something goes wrong:

1. **Check logs first:**
   ```bash
   sudo journalctl -u coderoad -n 100
   ```

2. **Restart services:**
   ```bash
   sudo systemctl restart coderoad
   docker restart postgres
   ```

3. **Verify configuration:**
   ```bash
   cat backend/.env
   cat backend/app/config.py | grep CORS
   ```

4. **Test Gemini API:**
   ```bash
   python3 test_gemini_api.py
   ```

---

## Success! 🎉

If all tests pass, you're live on AWS!

**What you've accomplished:**
- ✅ Frontend deployed to S3
- ✅ Backend running on EC2
- ✅ PostgreSQL database (handles WebSockets)
- ✅ Gemini API integrated
- ✅ Full application working
- ✅ Ready for users

**Total time:** 4-6 hours
**Total cost:** ~$25/month

---

**Questions?**
- Check AWS_DEPLOYMENT_GUIDE.md for detailed explanations
- Review DEPLOYMENT_CHECKLIST.md for day-by-day plan
- Run `python test_gemini_api.py` to verify API key

**Good luck! 🚀**
