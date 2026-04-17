# Update Vercel Environment Variables

## ✅ Migration Complete!
- Backend deployed to Render: https://coderoad-gmq6.onrender.com
- Database migrated: 3 players, 68 submissions, 82 challenges, 72 matches (239 total rows)
- Registration tested and working ✅

## Next Step: Update Vercel Environment Variables

### Go to Vercel Dashboard
1. Visit: https://vercel.com/dashboard
2. Click on your "code-road" project
3. Go to "Settings" tab
4. Click on "Environment Variables" in the left sidebar

### Update These Variables:

#### VITE_API_URL
- **Current Value**: `http://100.48.103.123:8000/api/v1`
- **New Value**: `https://coderoad-gmq6.onrender.com/api/v1`

#### VITE_WS_URL
- **Current Value**: `ws://100.48.103.123:8000/ws`
- **New Value**: `wss://coderoad-gmq6.onrender.com/ws`

### Apply to All Environments
Make sure to update for:
- ✅ Production
- ✅ Preview
- ✅ Development

### Redeploy
After updating the environment variables:
1. Go to "Deployments" tab
2. Click the "..." menu on the latest deployment
3. Click "Redeploy"
4. Wait 2-3 minutes for deployment to complete

### Test the Deployment
Once redeployed, visit your Vercel URL and test:
- ✅ Registration (create a new account)
- ✅ Login (with the new account)
- ✅ Dashboard loads
- ✅ Matchmaking works
- ✅ WebSocket connection works

## Current Status
- ✅ Render backend: LIVE at https://coderoad-gmq6.onrender.com
- ✅ PostgreSQL database: Migrated with all data
- ✅ Registration: Working
- ⏳ Vercel frontend: Needs environment variable update
- ⏳ DNS: Still pointing to AWS (will update after Vercel works)

## After Vercel Works
1. Update DNS on Hostinger to point to Vercel
2. Test coderoad.online domain
3. Stop AWS EC2 instance
4. Save $15-25/month! 🎉
