# Disable CloudFront Distribution

## Quick Steps

1. Go to AWS CloudFront Console: https://console.aws.amazon.com/cloudfront/
2. Find distribution: **E1SDADDHAQZFDE**
3. Click on the distribution ID
4. Click "Disable"
5. Wait 5-10 minutes for it to disable
6. Once disabled, you can delete it (optional)

## Why?

CloudFront is still serving the old site even though DNS now points to Vercel. Disabling it will allow the new DNS to take effect immediately.

## After Disabling

- Wait 5-10 minutes
- Clear your browser cache (Ctrl+Shift+Delete)
- Visit https://coderoad.online
- It should now load from Vercel with Render backend!

## Verification

Once CloudFront is disabled, test:
- Visit https://coderoad.online
- Check response headers (should see "x-vercel" instead of "x-amz-cf")
- Test login with existing user
- Test registration
- Test leaderboard (should show all 51 players)
