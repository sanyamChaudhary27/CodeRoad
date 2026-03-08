# AWS Cost & Usage Analysis
**Date**: March 6, 2026  
**Instance**: t3.small (2 vCPU, 2GB RAM)  
**Region**: us-east-1

---

## Current Resource Usage

### EC2 Instance (t3.small)
- **CPU Usage**: 0-3% (very low, idle most of the time)
- **Memory Usage**: 567MB / 1910MB (30% used)
- **Available Memory**: 1.1GB free
- **Disk Usage**: 4.3GB / 7.6GB (57% used, 3.3GB free)
- **Status**: ✅ Healthy, plenty of headroom

### Network
- **Active Connections**: 11 established TCP connections
- **Total Sockets**: 199 (normal for web server)
- **Status**: ✅ Low traffic, no congestion

### Database (PostgreSQL in Docker)
- **Container**: Running for 4+ hours
- **Size**: 274MB virtual, 63B actual usage
- **Status**: ✅ Minimal data stored

### Backend Service
- **Process**: Uvicorn with 2 workers
- **Memory per worker**: ~24MB
- **Status**: ✅ Running efficiently

---

## Cost Breakdown (Monthly Estimates)

### 1. EC2 - t3.small
- **On-Demand Rate**: $0.0208/hour
- **Monthly (730 hours)**: ~$15.18
- **Free Tier**: First 750 hours/month free for 12 months
- **Your Cost**: $0 (within free tier)

### 2. EBS Storage (8GB)
- **Rate**: $0.10/GB-month
- **Monthly**: $0.80
- **Free Tier**: 30GB free for 12 months
- **Your Cost**: $0 (within free tier)

### 3. Data Transfer
- **Current Usage**: Minimal (< 1GB/day estimated)
- **Rate**: First 100GB/month free, then $0.09/GB
- **Monthly Estimate**: ~30GB
- **Your Cost**: $0 (within free tier)

### 4. CloudFront CDN
- **Rate**: First 1TB/month free for 12 months
- **Current Usage**: < 1GB (frontend assets)
- **Your Cost**: $0 (within free tier)

### 5. S3 Storage (Frontend)
- **Rate**: $0.023/GB-month
- **Current Usage**: < 1MB (built frontend)
- **Monthly**: < $0.01
- **Free Tier**: 5GB free for 12 months
- **Your Cost**: $0 (within free tier)

### 6. Groq API (AI Generation)
- **Rate**: FREE tier
- **Limits**: 30 requests/minute per key × 5 keys = 150 req/min
- **Current Usage**: ~10-20 requests/hour
- **Your Cost**: $0

---

## Total Monthly Cost: $0.00
**All services are within AWS Free Tier limits**

---

## Capacity Analysis

### Current Load
- **Registered Users**: 3-5
- **Concurrent Users**: 1-2
- **Matches/Day**: ~10-20
- **API Calls/Day**: ~500-1000

### Maximum Capacity (Current Setup)
- **Concurrent Users**: 20-30 (before performance degrades)
- **Registered Users**: 500-1000 (database can handle)
- **Matches/Day**: 1000+ (Groq API limit is the bottleneck)
- **API Calls/Day**: 50,000+ (backend can handle)

### Bottlenecks
1. **Groq API**: 150 req/min = 9,000 req/hour = 216,000 req/day (plenty of headroom)
2. **Memory**: 1.1GB free (can handle 10-15 more concurrent users)
3. **CPU**: 97% idle (can handle 50x more load)

---

## Scaling Recommendations

### For 100 Users (Hackathon)
- **Current Setup**: ✅ Sufficient
- **Expected Cost**: $0 (still within free tier)
- **Action Needed**: None

### For 500 Users
- **Upgrade to**: t3.medium (2 vCPU, 4GB RAM)
- **Cost**: ~$30/month
- **When**: If you see memory usage > 80%

### For 1000+ Users
- **Upgrade to**: t3.large (2 vCPU, 8GB RAM)
- **Add**: RDS PostgreSQL (instead of Docker)
- **Add**: Load balancer (if needed)
- **Cost**: ~$80-100/month

---

## Cost Optimization Tips

1. **Stop EC2 when not in use**: Save ~$15/month (but you'll lose uptime)
2. **Use Reserved Instances**: Save 30-40% if you commit to 1 year
3. **Monitor CloudWatch**: Set billing alarms at $10, $50, $100
4. **Clean up old data**: Delete old matches/submissions after 30 days

---

## Budget Status

- **Total Budget**: $200 ($100 free tier + $100 credits)
- **Used So Far**: ~$0
- **Remaining**: $200
- **Burn Rate**: $0/month (within free tier)
- **Runway**: 12 months (free tier) + indefinite (with $200 credits)

---

## Monitoring Commands

Check resource usage anytime:
```bash
# CPU & Memory
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "top -bn1 | head -15"

# Disk
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "df -h"

# Active connections
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "ss -s"

# Backend logs
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "sudo journalctl -u coderoad -n 50"
```

---

## Conclusion

✅ **You're in great shape!**
- All services running efficiently
- Zero cost (within free tier)
- Plenty of capacity for 100+ users
- No immediate action needed

For the hackathon, you can safely invite 100 friends without worrying about costs or performance.
