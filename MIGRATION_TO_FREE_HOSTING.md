# Migration Guide: AWS to Free Hosting (Railway + Vercel)

## Overview
Migrate from AWS (EC2 + CloudFront + S3) to free hosting providers with zero downtime.

**Cost Savings**: ~$20-50/month → $0/month

## Architecture Change

### Before (AWS)
```
Frontend: S3 + CloudFront
Backend: EC2 (100.48.103.123)
Database: SQLite on EC2
Domain: coderoad.online → EC2
```

### After (Free Hosting)
```
Frontend: Vercel (with CDN)
Backend: Railway.app
Database: SQLite on Railway (or upgrade to PostgreSQL)
Domain: coderoad.online → Railway backend
```

## Prerequisites

1. **GitHub Repository**: Ensure code is pushed to GitHub
2. **Railway Account**: Sign up at https://railway.app (free with GitHub)
3. **Vercel Account**: Sign up at https://vercel.com (free with GitHub)
4. **Database Backup**: Download current database from EC2

## Phase 1: Deploy Backend to Railway

### Step 1: Backup Current Database
```bash
# SSH into EC2
ssh -i "C:\Users\HP\Downloads\coderoad-key.pem" ubuntu@100.48.103.123

# Backup database
cd ~/CodeRoad/backend
cp coderoad.db coderoad.db.backup.$(date +%Y%m%d)

# Download to local machine (from local terminal)
scp -i "C:\Users\HP\Downloads\coderoad-key.pem" ubuntu@100.48.103.123:~/CodeRoad/backend/coderoad.db ./coderoad.db.backup
```

### Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your CodeRoad repository
4. Railway will auto-detect Python and deploy

### Step 3: Configure Railway Environment Variables

In Railway dashboard → Variables tab, add:

```env
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
DATABASE_URL=sqlite:///./coderoad.db
GROQ_API_KEY=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
GROQ_API_KEY_2=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
GROQ_API_KEY_3=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
GROQ_API_KEY_4=gsk_TZClRWh8S2DSyE0kmaLgWGdyb3FYWZUdZkBDSbXhOTlHrx7jkPY
GROQ_API_KEY_5=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
PYTHONUNBUFFERED=1
PORT=8000
```

### Step 4: Upload Database to Railway

1. In Railway dashboard → Data tab
2. Upload `coderoad.db.backup` file
3. Or use Railway CLI:
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Upload database
railway run python -c "import shutil; shutil.copy('coderoad.db.backup', 'backend/coderoad.db')"
```

### Step 5: Get Railway Backend URL

After deployment, Railway provides a URL like:
```
https://coderoad-production.up.railway.app
```

Save this URL - you'll need it for frontend configuration.

### Step 6: Test Railway Backend

```bash
# Test health endpoint
curl https://your-railway-url.railway.app/api/v1/health

# Test authentication
curl https://your-railway-url.railway.app/api/v1/auth/me
```

## Phase 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Environment Variables

Create `frontend/.env.production`:
```env
VITE_API_URL=https://your-railway-url.railway.app/api/v1
VITE_WS_URL=wss://your-railway-url.railway.app/ws
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add Environment Variables in Vercel dashboard:
   - `VITE_API_URL`: `https://your-railway-url.railway.app/api/v1`
   - `VITE_WS_URL`: `wss://your-railway-url.railway.app/ws`

5. Click "Deploy"

### Step 3: Get Vercel URL

Vercel provides a URL like:
```
https://coderoad.vercel.app
```

### Step 4: Test Vercel Frontend

1. Open `https://coderoad.vercel.app`
2. Try logging in
3. Test matchmaking
4. Verify WebSocket connection

## Phase 3: Configure Custom Domain

### Option A: Point Domain to Railway (Backend + Frontend)

Railway can serve both backend and frontend:

1. In Railway dashboard → Settings → Domains
2. Add custom domain: `coderoad.online`
3. Update DNS records at Hostinger:
   ```
   Type: CNAME
   Name: @
   Value: your-project.up.railway.app
   ```

### Option B: Split Domain (Recommended)

**Backend on Railway subdomain:**
1. Railway dashboard → Add domain: `api.coderoad.online`
2. DNS at Hostinger:
   ```
   Type: CNAME
   Name: api
   Value: your-railway-project.up.railway.app
   ```

**Frontend on Vercel:**
1. Vercel dashboard → Settings → Domains
2. Add domain: `coderoad.online`
3. DNS at Hostinger:
   ```
   Type: A
   Name: @
   Value: 76.76.21.21 (Vercel IP)
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

4. Update frontend `.env.production`:
   ```env
   VITE_API_URL=https://api.coderoad.online/api/v1
   VITE_WS_URL=wss://api.coderoad.online/ws
   ```

### Step 5: Wait for DNS Propagation

DNS changes take 5-60 minutes. Check status:
```bash
# Check DNS
nslookup coderoad.online
nslookup api.coderoad.online

# Test SSL
curl https://coderoad.online
curl https://api.coderoad.online/api/v1/health
```

## Phase 4: Verify Migration

### Checklist

- [ ] Backend accessible at Railway URL
- [ ] Frontend accessible at Vercel URL
- [ ] Login works
- [ ] Matchmaking works
- [ ] WebSocket connection works
- [ ] Challenge generation works (Groq API)
- [ ] Database has all users and matches
- [ ] Custom domain points to new hosting
- [ ] SSL certificates active (auto-provided by Railway/Vercel)

### Test Commands

```bash
# Test backend
curl https://api.coderoad.online/api/v1/health

# Test frontend
curl https://coderoad.online

# Test WebSocket (use browser console)
const ws = new WebSocket('wss://api.coderoad.online/ws/test-match-id');
ws.onopen = () => console.log('Connected');
```

## Phase 5: Shutdown AWS Resources

**⚠️ ONLY AFTER CONFIRMING NEW DEPLOYMENT WORKS**

### Step 1: Stop EC2 Instance

```bash
# From AWS Console or CLI
aws ec2 stop-instances --instance-ids i-your-instance-id

# Or terminate (permanent)
aws ec2 terminate-instances --instance-ids i-your-instance-id
```

### Step 2: Delete CloudFront Distribution

1. AWS Console → CloudFront
2. Select distribution `E1SDADDHAQZFDE`
3. Disable → Wait → Delete

### Step 3: Clean Up S3 Bucket

1. Download any important files
2. Delete bucket or keep for backups (minimal cost: ~$0.02/month)

### Step 4: Release Elastic IP (if any)

1. AWS Console → EC2 → Elastic IPs
2. Release any unattached IPs to avoid charges

## Rollback Plan

If something goes wrong:

1. **Keep EC2 running** until new deployment is verified
2. **DNS rollback**: Change DNS back to EC2 IP (100.48.103.123)
3. **Database restore**: Copy backup back to EC2

## Cost Comparison

### AWS (Before)
- EC2 t2.micro: ~$8-10/month
- CloudFront: ~$1-5/month
- S3: ~$0.50/month
- Data transfer: ~$5-10/month
- **Total: ~$15-25/month**

### Free Hosting (After)
- Railway: $0 (500 hours/month free)
- Vercel: $0 (unlimited for personal projects)
- **Total: $0/month**

## Monitoring & Maintenance

### Railway
- Dashboard: https://railway.app/dashboard
- Logs: Real-time in dashboard
- Deployments: Auto-deploy on git push
- Metrics: CPU, Memory, Network usage

### Vercel
- Dashboard: https://vercel.com/dashboard
- Logs: Real-time in dashboard
- Deployments: Auto-deploy on git push
- Analytics: Page views, performance

## Troubleshooting

### Backend Not Starting on Railway
- Check logs in Railway dashboard
- Verify `Procfile` or `nixpacks.toml` is correct
- Ensure `requirements-prod.txt` has all dependencies
- Check environment variables are set

### Frontend Not Building on Vercel
- Check build logs in Vercel dashboard
- Verify `vercel.json` configuration
- Ensure environment variables are set
- Check `package.json` scripts

### Database Issues
- Ensure database file is uploaded to Railway
- Check file permissions
- Consider upgrading to PostgreSQL for better reliability

### WebSocket Connection Fails
- Verify Railway supports WebSocket (it does)
- Check CORS settings in backend
- Ensure WSS (not WS) is used in production

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Railway Discord: https://discord.gg/railway
- Vercel Discord: https://discord.gg/vercel

---

**Migration Timeline**: 1-2 hours
**Downtime**: 0 minutes (if done correctly)
**Difficulty**: Easy
**Cost Savings**: ~$15-25/month → $0
