#!/bin/bash

# Setup nginx with Let's Encrypt for CodeRoad
echo "Setting up nginx with Let's Encrypt for CodeRoad..."

# 1. Install nginx and certbot if not already installed
echo "Installing nginx and certbot..."
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Stop nginx temporarily
sudo systemctl stop nginx

# 3. Backup default nginx config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup 2>/dev/null || true

# 4. Copy our nginx config
echo "Copying nginx configuration..."
sudo cp ~/CodeRoad/nginx-coderoad.conf /etc/nginx/sites-available/coderoad

# 5. Enable the site
sudo ln -sf /etc/nginx/sites-available/coderoad /etc/nginx/sites-enabled/coderoad

# 6. Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# 7. Create temporary HTTP-only config for Let's Encrypt verification
echo "Creating temporary HTTP config for Let's Encrypt..."
sudo tee /etc/nginx/sites-available/coderoad-temp > /dev/null <<'EOF'
server {
    listen 80;
    server_name coderoad.online www.coderoad.online;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 200 "OK";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/coderoad-temp /etc/nginx/sites-enabled/coderoad-temp
sudo rm -f /etc/nginx/sites-enabled/coderoad

# 8. Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "✗ Nginx configuration test failed!"
    exit 1
fi

# 9. Start nginx with temporary config
echo "Starting nginx..."
sudo systemctl start nginx

# 10. Obtain Let's Encrypt certificate
echo ""
echo "Obtaining Let's Encrypt SSL certificate..."
echo "This will ask for your email and agreement to terms."
echo ""

sudo certbot certonly --nginx -d coderoad.online -d www.coderoad.online

if [ $? -eq 0 ]; then
    echo "✓ SSL certificate obtained successfully!"
    
    # 11. Switch to production config with SSL
    echo "Switching to production nginx config..."
    sudo rm -f /etc/nginx/sites-enabled/coderoad-temp
    sudo ln -sf /etc/nginx/sites-available/coderoad /etc/nginx/sites-enabled/coderoad
    
    # 12. Test nginx configuration again
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        # 13. Reload nginx
        sudo systemctl reload nginx
        sudo systemctl enable nginx
        
        echo ""
        echo "✓ Nginx setup complete!"
        echo ""
        echo "WebSocket URL: wss://coderoad.online/ws/"
        echo "API URL: https://coderoad.online/api/"
        echo ""
        echo "Certificate auto-renewal is configured via certbot."
        echo ""
        echo "To check nginx status: sudo systemctl status nginx"
        echo "To view logs: sudo tail -f /var/log/nginx/coderoad-error.log"
        echo "To test WebSocket: Check browser console in Arena page"
    else
        echo "✗ Nginx configuration test failed after SSL setup!"
        exit 1
    fi
else
    echo "✗ Failed to obtain SSL certificate!"
    echo "Make sure:"
    echo "1. DNS is pointing to this server (coderoad.online → $(curl -s ifconfig.me))"
    echo "2. Port 80 is open in AWS Security Group"
    echo "3. Domain is accessible from the internet"
    exit 1
fi
