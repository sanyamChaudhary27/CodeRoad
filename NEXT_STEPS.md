# Next Steps - Complete the Migration

## Current Status
✅ Code pushed to GitHub main branch
✅ Render is deploying backend with PostgreSQL
✅ PostgreSQL tables will be created automatically
⏳ Waiting for Render deployment to complete

## What You Need to Do Now

### 1. Monitor Render Deployment (5-10 minutes)
Go to: https://dashboard.render.com/
- Click on "coderoad-backend" service
- Watch the deployment logs
- Wait for "Live" status

### 2. Test Render Backend
Once deployment shows "Live", test the backend:
```bash
curl https://coderoad-gmq6.onrender.com/health
```

Should return: `{"status":"healthy"}`

### 3. Migrate Data from SQLite to PostgreSQL

**We need to upload the SQLite database to Render and run the migration.**

#### Option A: Using Render Shell (Easiest)
1. Go to Render Dashboard → coderoad-backend → Shell tab
2. In the shell, run:
   ```bash
   # Check if database file exists
   ls -la backend/coderoad.db
   
   # If it doesn't exist, we need to upload it
   # You can use the file upload feature in Render Shell
   ```

3. Upload `backend/coderoad.db` using Render's file upload
4. Run migration:
   ```bash
   cd backend
   python migrate_data.py coderoad.db $DATABASE_URL
   ```

#### Option B: Create Admin Endpoint (If Shell doesn't work)
I can create a temporary admin endpoint that accepts the SQLite file upload and migrates data.

### 4. Verify Data Migration
Test login with an existing user:
```bash
curl -X POST https://coderoad-gmq6.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

### 5. Update Vercel Environment Variables
Go to Vercel Dashboard → code-road project → Settings → Environment Variables

Update these variables:
- `VITE_API_URL` = `https://coderoad-gmq6.onrender.com/api/v1`
- `VITE_WS_URL` = `wss://coderoad-gmq6.onrender.com/ws`

Then redeploy:
- Go to Deployments tab
- Click "..." on latest deployment
- Click "Redeploy"

### 6. Test Vercel Frontend
Visit: https://code-road-7mvbpv7st-sanyamchaudhary27s-projects.vercel.app
- Try logging in with existing credentials
- Test registration
- Test matchmaking

### 7. Update DNS (Final Step)
Once everything works on Vercel:

Go to Hostinger DNS settings for coderoad.online:
1. **Remove** the A record pointing to `100.48.103.123`
2. **Add** CNAME record:
   - Name: `@` (or `coderoad.online`)
   - Value: `cname.vercel-dns.com`
3. Wait 5-10 minutes for DNS propagation

### 8. Final Verification
Visit https://coderoad.online
- Should now point to Vercel frontend
- Should connect to Render backend
- All 50 users should be able to log in

### 9. Stop AWS Resources (After 24 hours of testing)
Once you're confident everything works:
```bash
# Stop EC2 instance (don't terminate yet, just stop)
# This way you can restart if needed

# After 1 week of successful operation:
# - Terminate EC2 instance
# - Delete CloudFront distribution
# - Empty and delete S3 bucket
```

## Need Help?
Let me know which step you're on and I'll help you through it!

## Files to Keep Handy
- `backend/coderoad.db` - Your SQLite database with 50 users
- `DEPLOYMENT_SECRETS.md` - All credentials and connection strings
- `MIGRATION_STATUS.md` - Current migration status
