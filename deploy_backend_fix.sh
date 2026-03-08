#!/bin/bash
# Deploy backend profile picture fix

export PATH="/c/Program Files/Git/usr/bin:$PATH"

echo "Uploading fixed files to EC2..."
scp -i ~/.ssh/coderoad-key.pem backend/app/api/auth.py ubuntu@100.48.103.123:~/CodeRoad/backend/app/api/
scp -i ~/.ssh/coderoad-key.pem backend/app/schemas/player_schema.py ubuntu@100.48.103.123:~/CodeRoad/backend/app/schemas/

echo "Restarting backend service..."
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "sudo systemctl restart coderoad"

echo "Waiting for service to start..."
sleep 3

echo "Checking service status..."
ssh -i ~/.ssh/coderoad-key.pem ubuntu@100.48.103.123 "sudo systemctl status coderoad --no-pager -n 10"

echo ""
echo "Backend fix deployed! Try uploading profile picture again."
