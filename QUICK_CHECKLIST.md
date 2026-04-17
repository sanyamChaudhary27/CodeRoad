# Quick Migration Checklist

## Right Now (You're Here)
- [x] PostgreSQL database created on Render
- [x] Code pushed to GitHub
- [x] Render is deploying backend
- [ ] **WAIT FOR RENDER DEPLOYMENT TO COMPLETE** ← YOU ARE HERE

## Next (After Render shows "Live")
1. [ ] Test Render backend: `curl https://coderoad-gmq6.onrender.com/health`
2. [ ] Enable migration: Add `ENABLE_MIGRATION=true` in Render environment variables
3. [ ] Migrate data using admin endpoint or Render Shell
4. [ ] Verify login works on Render backend
5. [ ] Update Vercel environment variables
6. [ ] Redeploy Vercel frontend
7. [ ] Test everything on Vercel URL
8. [ ] Update DNS to point to Vercel
9. [ ] Test coderoad.online
10. [ ] Disable migration endpoint
11. [ ] Stop AWS EC2 instance (after 24 hours)

## Files You Need
- `backend/coderoad.db` - SQLite database with 50 users
- `DEPLOYMENT_SECRETS.md` - All credentials
- `DEPLOYMENT_COMPLETE_GUIDE.md` - Full instructions

## Quick Commands

### Test Render Backend
```bash
curl https://coderoad-gmq6.onrender.com/health
```

### Test Login
```bash
curl -X POST https://coderoad-gmq6.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

### Check Migration Status
```bash
curl https://coderoad-gmq6.onrender.com/api/v1/admin/migration-status
```

## What to Watch
- Render Dashboard: https://dashboard.render.com/
- Vercel Dashboard: https://vercel.com/dashboard
- Hostinger DNS: https://hpanel.hostinger.com/

## Current URLs
- **Render Backend**: https://coderoad-gmq6.onrender.com
- **Vercel Frontend**: https://code-road-7mvbpv7st-sanyamchaudhary27s-projects.vercel.app
- **Production Domain**: https://coderoad.online (still on AWS)

## Timeline
- Render deployment: 5-10 minutes
- Data migration: 5 minutes
- Vercel redeploy: 2-3 minutes
- DNS propagation: 5-60 minutes
- **Total**: ~30-90 minutes

## Success = $0/month hosting! 🎉
