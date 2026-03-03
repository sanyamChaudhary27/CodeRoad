# Code Road - Deployment Guide

## 🚀 Quick Start

### 1. Test Gemini API
```bash
python test_gemini_api.py
```

**If it hangs:** Check your API key and model name in the script.

### 2. Deploy to AWS (FREE Tier)
See: **AWS_FREE_TIER_DEPLOYMENT.md**

---

## 📚 Documentation Files

1. **AWS_FREE_TIER_DEPLOYMENT.md** - Deploy for FREE (12 months)
2. **QUICK_DEPLOY_GUIDE.md** - Fast deployment guide
3. **test_gemini_api.py** - Test your API key
4. **check_deployment_readiness.py** - Pre-deployment checks

---

## 💰 Cost: $0/month (FREE Tier)

- AWS Amplify: FREE (static sites)
- EC2 t3.micro: FREE (750 hours/month)
- PostgreSQL in Docker: FREE
- Total: $0 for 12 months!

---

## 🎯 Timeline

- March 2: ✅ Complete
- March 3: Deploy frontend
- March 4: Deploy backend  
- March 5: Testing
- March 6: Launch! 🚀

---

## 🆘 Troubleshooting

### Gemini API hanging?
The script uses `gemini-1.5-flash` model. If it hangs:
1. Check your API key in `backend/.env`
2. Try `gemini-1.5-pro` instead
3. Check internet connection
4. Verify API key has Gemini API enabled

### Quick fix:
```bash
# Edit test_gemini_api.py
# Change line 38 to:
model = genai.GenerativeModel('gemini-1.5-pro')
```

---

**For full instructions, see AWS_FREE_TIER_DEPLOYMENT.md**
