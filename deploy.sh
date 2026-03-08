#!/bin/bash
# CodeRoad Deployment Script for AWS EC2

set -e

echo "🚀 CodeRoad Deployment Script"
echo "=============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || ! grep -q ec2 /sys/hypervisor/uuid 2>/dev/null; then
    echo -e "${YELLOW}Warning: This script is designed for AWS EC2 instances${NC}"
fi

# Update system
echo -e "${GREEN}📦 Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo -e "${GREEN}📦 Installing dependencies...${NC}"
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Add user to docker group
sudo usermod -aG docker $USER

# Clone or update repository
if [ -d "CodeRoad" ]; then
    echo -e "${GREEN}📥 Updating repository...${NC}"
    cd CodeRoad
    git pull
else
    echo -e "${GREEN}📥 Cloning repository...${NC}"
    git clone https://github.com/sanyamChaudhary27/CodeRoad.git
    cd CodeRoad
fi

# Setup backend
echo -e "${GREEN}🔧 Setting up backend...${NC}"
cd backend

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}Error: .env.production not found!${NC}"
    echo "Please create .env.production with your configuration"
    exit 1
fi

# Copy production env
cp .env.production .env

# Install Python dependencies
pip3 install -r requirements-prod.txt

# Start PostgreSQL with Docker
echo -e "${GREEN}🐘 Starting PostgreSQL...${NC}"
docker run -d \
    --name coderoad-postgres \
    --restart unless-stopped \
    -e POSTGRES_DB=coderoad \
    -e POSTGRES_USER=coderoad \
    -e POSTGRES_PASSWORD=${DB_PASSWORD:-changeme} \
    -p 5432:5432 \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:15-alpine || echo "PostgreSQL container already running"

# Wait for PostgreSQL
echo -e "${GREEN}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 10

# Test database connection
python3 -c "from app.core.database import engine; engine.connect()" || {
    echo -e "${RED}Error: Cannot connect to database${NC}"
    exit 1
}

# Create systemd service
echo -e "${GREEN}⚙️  Creating systemd service...${NC}"
sudo tee /etc/systemd/system/coderoad.service > /dev/null <<EOF
[Unit]
Description=CodeRoad Backend
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=/home/$USER/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable coderoad
sudo systemctl restart coderoad

# Check service status
sleep 5
if sudo systemctl is-active --quiet coderoad; then
    echo -e "${GREEN}✅ Backend service started successfully${NC}"
else
    echo -e "${RED}❌ Backend service failed to start${NC}"
    sudo journalctl -u coderoad -n 50
    exit 1
fi

# Setup Nginx reverse proxy
echo -e "${GREEN}🌐 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/coderoad > /dev/null <<'EOF'
server {
    listen 80;
    server_name coderoad.online www.coderoad.online;

    # Frontend (will be added after S3 deployment)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/coderoad /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Update DNS records to point to this server's IP"
echo "2. Run: sudo certbot --nginx -d coderoad.online -d www.coderoad.online"
echo "3. Deploy frontend to S3/CloudFront"
echo ""
echo "Service status:"
sudo systemctl status coderoad --no-pager
echo ""
echo "Backend URL: http://$(curl -s ifconfig.me):8000"
echo "Health check: curl http://localhost:8000/health"
