#!/bin/bash
# NekoSvan CRM - Deploy Script
# Usage: ./deploy.sh [server_ip] [server_user]

set -e

SERVER_IP=${1:-"72.62.92.89"}
SERVER_USER=${2:-"root"}
APP_DIR="/opt/nekosvan"

echo "🚀 Deploying NekoSvan CRM to $SERVER_USER@$SERVER_IP"
echo ""

# Create deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR=$(mktemp -d)
rsync -av --exclude='venv' --exclude='node_modules' --exclude='.git' \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
    --exclude='frontend/dist' --exclude='*.sqlite3' \
    . "$DEPLOY_DIR/"

# Copy to server
echo "📤 Uploading to server..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p $APP_DIR"
rsync -avz --delete "$DEPLOY_DIR/" $SERVER_USER@$SERVER_IP:$APP_DIR/

# Setup on server
echo "⚙️  Setting up on server..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/nekosvan

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate random secret key
    SECRET_KEY=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    # Generate random DB password
    DB_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    sed -i "s/your-secure-database-password/$DB_PASS/" .env
    echo "Generated new .env file with random secrets"
fi

# Build and start
echo "🐳 Building and starting containers..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T backend python manage.py migrate --noinput

# Create superuser if not exists
docker-compose exec -T backend python manage.py shell << 'PYEOF'
from src.accounts.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@praut.cz', 'admin123', role='martin', is_master=True)
    print('Created admin superuser')
else:
    print('Admin user already exists')
PYEOF

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Application URLs:"
echo "   Frontend: http://$HOSTNAME:12666"
echo "   Backend:  http://$HOSTNAME:13666"
echo "   ONLYOFFICE: http://$HOSTNAME:9980"
echo ""
echo "🔑 Default login: admin / admin123"
echo "   (Change this immediately!)"
ENDSSH

# Cleanup
rm -rf "$DEPLOY_DIR"

echo ""
echo "🎉 Done! NekoSvan CRM deployed to $SERVER_IP"
