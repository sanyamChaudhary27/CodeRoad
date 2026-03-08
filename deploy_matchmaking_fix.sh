#!/bin/bash

# Deploy matchmaking fix to EC2
echo "Deploying matchmaking fix..."

# Upload fixed match_service.py
scp -i "C:\Users\HP\Downloads\coderoad-key.pem" backend/app/services/match_service.py ubuntu@100.48.103.123:~/coderoad/backend/app/services/

# Restart backend service
ssh -i "C:\Users\HP\Downloads\coderoad-key.pem" ubuntu@100.48.103.123 << 'EOF'
cd ~/coderoad/backend
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Restart service
sudo systemctl restart coderoad-backend
sleep 3
sudo systemctl status coderoad-backend --no-pager -l

echo "✓ Backend restarted"
EOF

echo "✓ Deployment complete"
