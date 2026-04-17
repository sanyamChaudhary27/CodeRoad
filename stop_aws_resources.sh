#!/bin/bash

# Stop AWS Resources to Save Costs
# Run this after Vercel deployment is confirmed working

echo "=== Stopping AWS Resources ==="

# EC2 Instance
EC2_INSTANCE_ID="i-0a234567890abcdef"  # Replace with actual instance ID
EC2_REGION="us-east-1"

# CloudFront Distribution
CLOUDFRONT_DIST_ID="E1SDADDHAQZFDE"

echo ""
echo "1. Stopping EC2 Instance..."
echo "   Instance ID: $EC2_INSTANCE_ID"
echo "   Region: $EC2_REGION"
echo ""
echo "Run this command:"
echo "aws ec2 stop-instances --instance-ids $EC2_INSTANCE_ID --region $EC2_REGION"
echo ""

echo "2. Disabling CloudFront Distribution..."
echo "   Distribution ID: $CLOUDFRONT_DIST_ID"
echo ""
echo "First, get the current config:"
echo "aws cloudfront get-distribution-config --id $CLOUDFRONT_DIST_ID > cf-config.json"
echo ""
echo "Then disable it (requires editing JSON to set Enabled: false):"
echo "aws cloudfront update-distribution --id $CLOUDFRONT_DIST_ID --if-match <ETag> --distribution-config file://cf-config-disabled.json"
echo ""
echo "After disabled, delete it:"
echo "aws cloudfront delete-distribution --id $CLOUDFRONT_DIST_ID --if-match <ETag>"
echo ""

echo "3. Verify EC2 is stopped:"
echo "aws ec2 describe-instances --instance-ids $EC2_INSTANCE_ID --region $EC2_REGION --query 'Reservations[0].Instances[0].State.Name'"
echo ""

echo "=== Cost Savings ==="
echo "After stopping these resources, you'll save approximately:"
echo "- EC2 t2.micro: ~\$8-10/month"
echo "- CloudFront: ~\$5-15/month (depending on traffic)"
echo "- Total savings: ~\$15-25/month"
echo ""
echo "New hosting costs:"
echo "- Render (backend): \$0/month (free tier)"
echo "- Vercel (frontend): \$0/month (free tier)"
echo "- Total: \$0/month"
echo ""
