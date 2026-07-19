# Render Migration Guide

## Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Configure PostgreSQL for Render deployment"
git push CodeRoad main
```

## Step 2: Render Will Auto-Deploy

Render will automatically:
1. Install dependencies from `requirements-render.txt`
2. Run `init_db.py` to create tables in PostgreSQL
3. Start the backend with `uvicorn`

## Step 3: Migrate Data from SQLite to PostgreSQL

After Render deployment completes, we need to migrate the data. We'll do this by:

### Option A: Use Render Shell (Recommended)

1. Go to Render Dashboard → coderoad-backend → Shell
2. Upload the SQLite database file
3. Run the migration script

### Option B: API-based Migration

Create a temporary admin endpoint to trigger migration from the SQLite backup.

## Step 4: Update Frontend Environment Variables

Update Vercel environment variables:
- `VITE_API_URL=https://coderoad-gmq6.onrender.com/api/v1`
- `VITE_WS_URL=wss://coderoad-gmq6.onrender.com/ws`

## Step 5: Update DNS

Point coderoad.online to Vercel frontend:
- Remove A record pointing to EC2
- Add CNAME record pointing to Vercel

## Step 6: Test Everything

1. Test login/registration
2. Test matchmaking
3. Test WebSocket connections
4. Verify all 50 users can log in

## Step 7: Stop AWS Resources

Once everything works:
1. Stop EC2 instance
2. Delete CloudFront distribution
3. Empty and delete S3 bucket

## Database Connection Details

Copy the current external or internal URL from the Render dashboard directly
into the destination service's `DATABASE_URL` environment variable. Never put
database credentials in this repository or in screenshots.
