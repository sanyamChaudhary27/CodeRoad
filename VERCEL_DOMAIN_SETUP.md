# Vercel Domain Setup & AWS Shutdown Guide

## Current Status
- ✅ Backend: Deployed on Render at https://coderoad-gmq6.onrender.com
- ✅ Frontend: Deployed on Vercel at https://code-road-7mvbpv7st-sanyamchaudhary27s-projects.vercel.app
- ⏳ Domain: coderoad.online (currently pointing to AWS)
- ⏳ AWS: EC2 + CloudFront still running (costing $15-25/month)

## Step 1: Add Custom Domain to Vercel

1. Go to Vercel dashboard: https://vercel.com/dashboard
2. Click on your project: `code-road`
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `coderoad.online`
6. Click **Add**
7. Vercel will show you DNS records to configure

## Step 2: Configure DNS in Hostinger

1. Log into Hostinger: https://hpanel.hostinger.com
2. Go to **Domains** → **coderoad.online** → **DNS / Name Servers**
3. Delete or update existing A records pointing to AWS
4. Add these records (Vercel will show exact values):

### For Vercel:
```
Type: A
Name: @
Value: 76.76.21.21
TTL: 3600

Type: CNAME  
Name: www
Value: cname.vercel-dns.com
TTL: 3600
```

5. Save changes
6. Wait 5-10 minutes for DNS propagation
7. Go back to Vercel and click **Refresh** to verify

## Step 3: Test New Deployment

Before shutting down AWS, test that everything works:

1. Visit: https://coderoad.online (should load Vercel frontend)
2. Try logging in
3. Try creating a match
4. Check WebSocket connection works
5. Verify all features work

## Step 4: Stop AWS EC2 Instance

**Option A: Using AWS Console**
1. Go to AWS Console: https://console.aws.amazon.com/ec2
2. Select region: **US East (N. Virginia)**
3. Go to **Instances**
4. Find instance: `coderoad-backend` (IP: 100.48.103.123)
5. Right-click → **Instance State** → **Stop Instance**
6. Confirm

**Option B: Using AWS CLI**
```bash
# First, find your instance ID
aws ec2 describe-instances --region us-east-1 --filters "Name=ip-address,Values=100.48.103.123" --query 'Reservations[0].Instances[0].InstanceId'

# Then stop it (replace with actual instance ID)
aws ec2 stop-instances --instance-ids i-XXXXXXXXX --region us-east-1
```

## Step 5: Disable CloudFront Distribution

**Using AWS Console:**
1. Go to CloudFront: https://console.aws.amazon.com/cloudfront
2. Find distribution: `E1SDADDHAQZFDE`
3. Click on it
4. Click **Disable**
5. Wait for status to change to "Disabled" (takes 15-20 minutes)
6. Then click **Delete**

**Using AWS CLI:**
```bash
# Get current config
aws cloudfront get-distribution-config --id E1SDADDHAQZFDE > cf-config.json

# Edit cf-config.json and set "Enabled": false
# Then update:
aws cloudfront update-distribution --id E1SDADDHAQZFDE --if-match <ETag-from-config> --distribution-config file://cf-config.json

# After disabled, delete:
aws cloudfront delete-distribution --id E1SDADDHAQZFDE --if-match <ETag>
```

## Step 6: Verify Cost Savings

Check your AWS billing dashboard after 24 hours:
- EC2 charges should stop
- CloudFront charges should stop
- Expected savings: **$15-25/month**

## Rollback Plan (If Needed)

If something goes wrong:
1. Start EC2 instance again in AWS Console
2. Update DNS back to EC2 IP: 100.48.103.123
3. Wait for DNS propagation
4. Debug the issue

## New Architecture

**Before (AWS):**
- Frontend: S3 + CloudFront → $5-15/month
- Backend: EC2 t2.micro → $8-10/month
- **Total: $15-25/month**

**After (Free Hosting):**
- Frontend: Vercel (free tier) → $0/month
- Backend: Render (free tier) → $0/month
- **Total: $0/month**

## Important Notes

1. **Render free tier limitations:**
   - Spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds
   - 750 hours/month free (enough for 24/7)

2. **Vercel free tier limitations:**
   - 100 GB bandwidth/month
   - Unlimited deployments
   - Custom domains included

3. **Keep AWS account active:**
   - Don't delete the EC2 instance, just stop it
   - You can restart it anytime if needed
   - Stopped instances don't incur charges (except EBS storage ~$1/month)

## Troubleshooting

**If domain doesn't work after DNS update:**
- Clear browser cache
- Try incognito mode
- Check DNS propagation: https://dnschecker.org
- Wait up to 24 hours for full propagation

**If backend is slow:**
- Render free tier spins down after inactivity
- First request wakes it up (30-60 seconds)
- Consider upgrading to Render paid tier ($7/month) for always-on

**If WebSocket doesn't connect:**
- Check CORS settings in backend
- Verify WSS URL in frontend env vars
- Check Render logs for errors
