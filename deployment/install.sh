#!/bin/bash

# FreeUltraCV Installation Script
# ================================
# This script sets up FreeUltraCV on a Linux server
# Run as: sudo bash install.sh

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  FreeUltraCV Installation Script${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

# Variables
PROJECT_DIR="/var/www/freultracv"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/freultracv"
RUN_DIR="/var/run/freultracv"

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Welcome message
echo "This script will install and configure FreeUltraCV."
echo "Project directory: $PROJECT_DIR"
echo ""

# Confirm installation
read -p "Continue? [y/N]: " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "Step 1: Updating system..."
# Update system
apt-get update -qq
apt-get upgrade -y -qq

print_status "System updated"

echo ""
echo "Step 2: Installing dependencies..."

# Install Python and pip
apt-get install -y python3 python3-pip python3-venv python3-dev

# Install build dependencies
apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    fontconfig \
    libfreetype6 \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libwebp-dev

# Install WeasyPrint dependencies
apt-get install -y \
    libcairo2 \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

print_status "Dependencies installed"

echo ""
echo "Step 3: Creating project directory..."

# Create directory structure
mkdir -p "$PROJECT_DIR"
mkdir -p "$BACKEND_DIR"
mkdir -p "$FRONTEND_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$RUN_DIR"
mkdir -p "$BACKEND_DIR/exports"
mkdir -p "$BACKEND_DIR/uploads"

print_status "Directory structure created"

echo ""
echo "Step 4: Setting up Python virtual environment..."

# Create virtual environment
python3 -m venv "$VENV_DIR"

# Activate and upgrade pip
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

print_status "Virtual environment created"

echo ""
echo "Step 5: Installing Python packages..."

# Install Python packages
pip install -r "$BACKEND_DIR/requirements.txt"

print_status "Python packages installed"

echo ""
echo "Step 6: Setting up environment file..."

# Create environment file
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    
    # Generate secure keys
    SECRET_KEY=$(openssl rand -hex 64)
    JWT_SECRET=$(openssl rand -hex 64)
    
    # Update env file
    sed -i "s|your-secret-key-here|$SECRET_KEY|g" "$BACKEND_DIR/.env"
    sed -i "s|your-jwt-secret-key-change-in-production|$JWT_SECRET|g" "$BACKEND_DIR/.env"
    
    print_status "Environment file created with secure keys"
else
    print_warning "Environment file already exists, skipping..."
fi

echo ""
echo "Step 7: Initializing database..."

# Initialize database
cd "$BACKEND_DIR"
source "$VENV_DIR/bin/activate"

# Run migrations
export FLASK_APP=app.py
flask db init 2>/dev/null || true
flask db migrate -m "Initial migration"
flask db upgrade

print_status "Database initialized"

echo ""
echo "Step 8: Setting up file permissions..."

# Set permissions
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
chmod -R 775 "$BACKEND_DIR/exports"
chmod -R 775 "$BACKEND_DIR/uploads"
chmod -R 775 "$LOG_DIR"
chmod -R 775 "$RUN_DIR"

print_status "File permissions set"

echo ""
echo "Step 9: Creating systemd service..."

# Create systemd service file
cat > /etc/systemd/system/freultracv.service << 'EOF'
[Unit]
Description=FreeUltraCV Resume Builder
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/freultracv/backend
Environment="PATH=/var/www/freultracv/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/freultracv/venv/bin/gunicorn -c /var/www/freultracv/deployment/gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

print_status "Systemd service created"

echo ""
echo "Step 10: Setting up Nginx..."

# Install Nginx if not installed
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
fi

# Copy Nginx configuration
cp "$PROJECT_DIR/deployment/nginx.conf" /etc/nginx/sites-available/freultracv

# Enable site
ln -sf /etc/nginx/sites-available/freultracv /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

print_status "Nginx configured"

echo ""
echo "Step 11: Setting up firewall..."

# Configure firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

print_status "Firewall configured"

echo ""
echo "Step 12: Starting services..."

# Start and enable services
systemctl enable freultracv
systemctl start freultracv
systemctl restart nginx

print_status "Services started"

echo ""
echo "============================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "============================================"
echo ""
echo "FreeUltraCV is now installed and running!"
echo ""
echo "Important Information:"
echo "----------------------"
echo "• Admin Panel: http://your-domain/admin.html"
echo "• API: http://your-domain/api"
echo "• Admin Credentials:"
echo "  Email: admin@freultracv.com"
echo "  Password: admin123"
echo ""
echo "Next Steps:"
echo "1. Change the admin password immediately!"
echo "2. Update your domain in /etc/nginx/sites-available/freultracv"
echo "3. Set up SSL with Let's Encrypt:"
echo "   certbot --nginx -d your-domain.com"
echo "4. Monitor logs:"
echo "   tail -f /var/log/freultracv/error.log"
echo ""
echo "Useful Commands:"
echo "• Restart: systemctl restart freultracv"
echo "• Status: systemctl status freultracv"
echo "• Logs: journalctl -u freultracv -f"
echo ""
