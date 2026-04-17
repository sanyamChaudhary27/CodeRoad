# Migration Status - Render + Vercel Deployment

## ✅ Completed Steps

### 1. PostgreSQL Database Setup
- Created PostgreSQL database on Render
- Connection details saved in DEPLOYMENT_SECRETS.md
- Database URL: `postgresql://coderoad:sx24AaBRZyLk5LmPLx1000xxrqd8l1LBb@dpg-d7h3b4eqvct57bts8hg-a.oregon-postgres.render.com/coderoad`

### 2. Backend Configuration
- Updated `render.yaml` with PostgreSQL DATABASE_URL
- Created `backend/init_db.py` to initialize tables
- Created `backend/requirements-render.txt` with necessary dependencies
- Created `backend/migrate_data.py` for data migration
- Pushed to main branch - Render is now deploying

### 3. Database Backup
- Original SQLite database safe at `backend/coderoad.db` (50 users)
- Local backup exists

### 4. Migration Scripts
- `migrate_to_postgres.py` - Local migration script (SSL issues from Windows)
- `backend/migrate_data.py` - Server-side migration script (to run on Render)

## 🔄 In Progress

### Render Deployment
- Render is currently deploying the backend
- Will create PostgreSQL tables automatically via `init_db.py`
- Backend URL: https://coderoad-gmq6.onrender.com

## ⏳ Next Steps

### Step 1: Wait for Render Deployment
Monitor Render dashboard for deployment completion

### Step 2: Migrate Data to PostgreSQL
After Render deployment completes, we need to upload the SQLite database and run migration:

**Option A: Using Render Shell**
1. Go to Render Dashboard → coderoad-backend → Shell
2. Upload `backend/coderoad.db` file
3. Run: `python migrate_data.py coderoad.db $DATABASE_URL`

**Option B: Create Temporary Admin Endpoint**
Create an endpoint that accepts the SQLite file and migrates data

### Step 3: Update Vercel Environment Variables
```
VITE_API_URL=https://coderoad-gmq6.onrender.com/api/v1
VITE_WS_URL=wss://coderoad-gmq6.onrender.com/ws
```

### Step 4: Rebuild and Deploy Frontend on Vercel
```bash
cd frontend
npm run build
# Vercel will auto-deploy from main branch
```

### Step 5: Update DNS on Hostinger
- Remove A record pointing to EC2 (100.48.103.123)
- Add CNAME record: `coderoad.online` → `[your-vercel-domain].vercel.app`

### Step 6: Test Everything
1. Visit https://coderoad.online
2. Test login with existing users
3. Test registration
4. Test matchmaking
5. Test WebSocket connections
6. Verify all features work

### Step 7: Stop AWS Resources (After Verification)
```bash
# Stop EC2 instance
# Delete CloudFront distribution E1SDADDHAQZFDE
# Empty and delete S3 bucket
```

## 💰 Cost Savings
- Current AWS cost: $15-25/month
- New cost: $0/month (Render free tier + Vercel free tier)
- Savings: $180-300/year

## 🔐 Important Notes
- Database has 50 users - cannot lose data
- Site currently running on AWS with all data intact
- PostgreSQL database created but empty (waiting for migration)
- All credentials in DEPLOYMENT_SECRETS.md

## 📊 Current State
- **AWS**: Still running (EC2 + CloudFront + S3)
- **Render**: Deploying backend with PostgreSQL (empty database)
- **Vercel**: Frontend deployed but pointing to old AWS backend
- **DNS**: Still pointing to AWS (A record to EC2)

## 🎯 Goal
Migrate from AWS to Render + Vercel without losing any user data.
