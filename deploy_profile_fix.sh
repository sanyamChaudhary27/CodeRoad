#!/bin/bash
# Deploy profile picture fix with database migration

export PATH="/c/Program Files/Git/usr/bin:$PATH"

KEY="C:\Users\HP\Downloads\coderoad-key.pem"
SERVER="ubuntu@100.48.103.123"

echo "=== Uploading fixed files to EC2 ==="
scp -i "$KEY" backend/app/models/player.py $SERVER:~/CodeRoad/backend/app/models/
scp -i "$KEY" backend/app/api/auth.py $SERVER:~/CodeRoad/backend/app/api/
scp -i "$KEY" backend/app/schemas/player_schema.py $SERVER:~/CodeRoad/backend/app/schemas/
scp -i "$KEY" backend/migrate_profile_picture.py $SERVER:~/CodeRoad/backend/

echo ""
echo "=== Running database migration ==="
ssh -i "$KEY" $SERVER "cd ~/CodeRoad/backend && python3 migrate_profile_picture.py"

echo ""
echo "=== Restarting backend service ==="
ssh -i "$KEY" $SERVER "sudo systemctl restart coderoad"

echo ""
echo "Waiting for service to start..."
sleep 3

echo ""
echo "=== Checking service status ==="
ssh -i "$KEY" $SERVER "sudo systemctl status coderoad --no-pager -n 10"

echo ""
echo "=== Testing health endpoint ==="
ssh -i "$KEY" $SERVER "curl -s http://localhost:8000/api/v1/health"

echo ""
echo ""
echo "✓ Deployment complete! Try uploading your profile picture now."
