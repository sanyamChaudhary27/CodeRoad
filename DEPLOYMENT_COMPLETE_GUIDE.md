# Complete Deployment Guide - AWS to Render + Vercel

## 🎯 Goal
Migrate CodeRoad from AWS (EC2 + CloudFront + S3) to free hosting (Render + Vercel) while preserving all 50 users' data.

## ✅ What's Done

### 1. Backend Configuration
- ✅ PostgreSQL database created on Render
- ✅ `render.yaml` configured with PostgreSQL connection
- ✅ `backend/init_db.py` created for table initialization
- ✅ `backend/requirements-render.txt` with dependencies
- ✅ CORS updated to include Render URL
- ✅ Code pushed to GitHub main branch
- ✅ Render is auto-deploying

### 2. Migration Scripts
- ✅ `backend/migrate_data.py` - Server-side migration script
- ✅ `backend/app/api/admin_migration.py` - Admin endpoint for migration
- ✅ Local backup of SQLite database at `backend/coderoad.db`

### 3. Frontend
- ✅ Vercel deployment working
- ⏳ Needs environment variable update (after backend is ready)

## 📋 Step-by-Step Instructions

### STEP 1: Wait for Render Deployment (Current Step)
**Time: 5-10 minutes**

1. Go to https://dashboard.render.com/
2. Click on "coderoad-backend" service
3. Watch deployment logs
4. Wait for status to show "Live"

### STEP 2: Verify Render Backend is Running
**Time: 1 minute**

Test the health endpoint:
```bash
curl https://coderoad-gmq6.onrender.com/health
```

Expected response:
```json
{"status":"healthy","service":"code-road-backend","version":"1.0.0"}
```

### STEP 3: Migrate Data to PostgreSQL
**Time: 5 minutes**

**Option A: Using Admin Endpoint (Recommended)**

1. First, enable migration by adding environment variable in Render:
   - Go to Render Dashboard → coderoad-backend → Environment
   - Add: `ENABLE_MIGRATION=true`
   - Save (this will redeploy)

2. After redeploy, use the migration endpoint:
   ```bash
   # You'll need to login first to get a token
   # Then upload the SQLite file
   curl -X POST https://coderoad-gmq6.onrender.com/api/v1/admin/migrate-database \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@backend/coderoad.db"
   ```

**Option B: Using Render Shell**

1. Go to Render Dashboard → coderoad-backend → Shell
2. Upload `backend/coderoad.db` file
3. Run:
   ```bash
   cd backend
   python migrate_data.py coderoad.db $DATABASE_URL
   ```

### STEP 4: Verify Data Migration
**Time: 2 minutes**

Test login with an existing user:
```bash
curl -X POST https://coderoad-gmq6.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}'
```

Should return a JWT token if successful.

### STEP 5: Update Vercel Environment Variables
**Time: 3 minutes**

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Update these variables:
   - `VITE_API_URL` = `https://coderoad-gmq6.onrender.com/api/v1`
   - `VITE_WS_URL` = `wss://coderoad-gmq6.onrender.com/ws`
5. Go to Deployments tab
6. Click "..." on latest deployment → "Redeploy"

### STEP 6: Test Vercel Frontend
**Time: 5 minutes**

1. Visit: https://code-road-7mvbpv7st-sanyamchaudhary27s-projects.vercel.app
2. Test login with existing credentials
3. Test registration
4. Test matchmaking
5. Test WebSocket connections (opponent code sync)

### STEP 7: Update DNS to Point to Vercel
**Time: 10 minutes (including DNS propagation)**

1. Go to Hostinger DNS settings for coderoad.online
2. **Remove** A record pointing to `100.48.103.123`
3. **Add** CNAME record:
   - Type: CNAME
   - Name: `@` or `coderoad.online`
   - Value: `cname.vercel-dns.com`
4. Save changes
5. Wait 5-10 minutes for DNS propagation

### STEP 8: Final Verification
**Time: 10 minutes**

1. Visit https://coderoad.online (should now point to Vercel)
2. Test all features:
   - Login with existing users
   - Registration
   - DSA Arena matchmaking
   - Debug Arena
   - Leaderboard
   - Profile stats
   - WebSocket sync
3. Ask other users to test

### STEP 9: Disable Migration Endpoint
**Time: 1 minute**

For security, disable the migration endpoint:
1. Go to Render Dashboard → coderoad-backend → Environment
2. Change `ENABLE_MIGRATION` to `false` or remove it
3. Save

### STEP 10: Stop AWS Resources (After 24-48 hours)
**Time: 10 minutes**

Once you're confident everything works:

1. **Stop EC2 instance** (don't terminate yet):
   ```bash
   # From AWS Console or CLI
   aws ec2 stop-instances --instance-ids i-your-instance-id
   ```

2. **After 1 week of successful operation**:
   - Terminate EC2 instance
   - Delete CloudFront distribution E1SDADDHAQZFDE
   - Empty and delete S3 bucket

## 💰 Cost Savings
- **Before**: $15-25/month (AWS)
- **After**: $0/month (Render free + Vercel free)
- **Annual Savings**: $180-300

## 🔐 Security Notes
- Migration endpoint is protected by authentication
- Set `ENABLE_MIGRATION=false` after migration
- Consider deleting `backend/app/api/admin_migration.py` after migration
- Keep `DEPLOYMENT_SECRETS.md` secure and never commit to public repo

## 📊 Architecture
- **Frontend**: Vercel (React + Vite)
- **Backend**: Render (FastAPI + Uvicorn)
- **Database**: Render PostgreSQL (free tier)
- **Domain**: Hostinger DNS → Vercel
- **WebSocket**: Render (wss://)

## 🆘 Troubleshooting

### Render deployment fails
- Check logs in Render Dashboard
- Verify `requirements-render.txt` has all dependencies
- Check environment variables are set correctly

### Migration fails
- Verify PostgreSQL connection string is correct
- Check if tables were created (visit `/health` endpoint)
- Try Option B (Render Shell) if Option A fails

### Frontend can't connect to backend
- Verify CORS origins include Vercel URL
- Check environment variables in Vercel
- Test backend health endpoint directly

### DNS not updating
- DNS propagation can take up to 48 hours
- Use `nslookup coderoad.online` to check
- Clear browser cache and try incognito mode

## 📞 Need Help?
Check these files:
- `MIGRATION_STATUS.md` - Current status
- `NEXT_STEPS.md` - Detailed next steps
- `DEPLOYMENT_SECRETS.md` - All credentials
- `RENDER_MIGRATION_GUIDE.md` - Migration details

## ✨ Success Criteria
- [ ] Render backend is live and healthy
- [ ] All 50 users migrated to PostgreSQL
- [ ] Users can log in successfully
- [ ] Matchmaking works
- [ ] WebSocket connections work
- [ ] Vercel frontend deployed
- [ ] DNS points to Vercel
- [ ] coderoad.online works end-to-end
- [ ] AWS resources stopped
