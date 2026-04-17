# Quick Migration Steps (15 Minutes)

## 1. Backup Database (2 min)
```bash
scp -i "C:\Users\HP\Downloads\coderoad-key.pem" ubuntu@100.48.103.123:~/CodeRoad/backend/coderoad.db ./coderoad.db.backup
```

## 2. Deploy Backend to Railway (5 min)

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select CodeRoad repository
4. Add environment variables (copy from `backend/railway.env.example`)
5. Upload database file
6. Copy Railway URL: `https://your-app.up.railway.app`

## 3. Deploy Frontend to Vercel (5 min)

1. Go to https://vercel.com/new
2. Import CodeRoad repository
3. Set Root Directory: `frontend`
4. Add environment variables:
   ```
   VITE_API_URL=https://your-railway-url.railway.app/api/v1
   VITE_WS_URL=wss://your-railway-url.railway.app/ws
   ```
5. Deploy
6. Copy Vercel URL: `https://coderoad.vercel.app`

## 4. Test New Deployment (2 min)

- Open Vercel URL
- Login
- Start a match
- Verify everything works

## 5. Update DNS (1 min)

**At Hostinger DNS:**

For backend:
```
Type: CNAME
Name: api
Value: your-railway-app.up.railway.app
```

For frontend:
```
Type: A
Name: @
Value: 76.76.21.21
```

## 6. Wait & Verify (5-30 min)

Wait for DNS propagation, then test:
- https://coderoad.online
- https://api.coderoad.online/api/v1/health

## 7. Shutdown AWS (After verification)

1. Stop EC2 instance
2. Delete CloudFront distribution
3. Done! Saving $15-25/month

---

**Total Time**: 15 minutes + DNS propagation
**Downtime**: 0 minutes
**Cost**: $0/month
