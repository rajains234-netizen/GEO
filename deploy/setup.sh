#!/bin/bash
# GEO Score SaaS — VPS Bootstrap Script
# Run on a fresh Ubuntu 22.04+ VPS as root
set -e

DOMAIN="geoscore.ai"
APP_DIR="/var/www/geo"
APP_USER="geo"

echo "=== GEO Score SaaS — Server Setup ==="

# 1. System packages
echo "Installing system packages..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv redis-server nginx certbot python3-certbot-nginx curl git

# 2. Install Node.js (for building frontend)
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# 3. Create app user
echo "Creating app user..."
useradd -m -s /bin/bash $APP_USER || true

# 4. Clone or copy project
echo "Setting up application directory..."
mkdir -p $APP_DIR
# Copy your project files to $APP_DIR (or git clone)
# cp -r /path/to/GEO/* $APP_DIR/
chown -R $APP_USER:$APP_USER $APP_DIR

# 5. Python virtual environment
echo "Setting up Python environment..."
cd $APP_DIR
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER ./venv/bin/pip install --upgrade pip
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt

# 6. Build React frontend
echo "Building frontend..."
cd $APP_DIR/frontend
sudo -u $APP_USER npm install
sudo -u $APP_USER npm run build

# 7. Create reports directory
mkdir -p $APP_DIR/reports
chown $APP_USER:$APP_USER $APP_DIR/reports

# 8. Install systemd services
echo "Installing systemd services..."
cp $APP_DIR/deploy/geo-api.service /etc/systemd/system/
cp $APP_DIR/deploy/geo-worker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable geo-api geo-worker redis

# 9. Configure Nginx
echo "Configuring Nginx..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/geoscore
ln -sf /etc/nginx/sites-available/geoscore /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# 10. SSL with Let's Encrypt
echo "Setting up SSL..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || echo "SSL setup skipped — configure DNS first"

# 11. Start services
echo "Starting services..."
systemctl start redis
systemctl start geo-api
systemctl start geo-worker
systemctl restart nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Copy your .env file to $APP_DIR/.env"
echo "  2. Set up Stripe webhook: https://$DOMAIN/api/webhook"
echo "  3. Configure DNS A record: $DOMAIN -> your server IP"
echo "  4. Test: curl https://$DOMAIN/api/health"
echo ""
echo "Service management:"
echo "  systemctl status geo-api"
echo "  systemctl status geo-worker"
echo "  journalctl -u geo-api -f    # API logs"
echo "  journalctl -u geo-worker -f # Worker logs"
