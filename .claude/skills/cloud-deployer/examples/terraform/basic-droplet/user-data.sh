#!/bin/bash
# ==============================================================================
# User Data Script for Initial Droplet Setup
# ==============================================================================
# This script runs automatically on first boot

set -e

echo "=========================================="
echo "Initial Droplet Setup"
echo "=========================================="
echo ""

# Update system
echo "[1/5] Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git software-properties-common

# Install Docker
echo "[2/5] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
echo "[3/5] Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Python and pip
echo "[4/5] Installing Python..."
apt-get install -y -qq python3 python3-pip python3-venv

# Configure UFW firewall
echo "[5/5] Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable

# Create application directory
mkdir -p /opt/app
cd /opt/app

# Create sample web application
cat > app.py << 'EOF'
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from datetime import datetime

class HealthCheckHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'droplet': 'DigitalOcean Droplet'
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>DigitalOcean Droplet</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #0069ff; }
        .info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Welcome to DigitalOcean!</h1>
    <div class="info">
        <p><strong>Droplet:</strong> Successfully deployed with Terraform</p>
        <p><strong>Status:</strong> Running</p>
        <p><strong>Time:</strong> ''' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + '''</p>
    </div>
    <p>Check <a href="/health">/health</a> for health status.</p>
</body>
</html>
'''
            self.wfile.write(html.encode())
        else:
            super().do_GET()

if __name__ == '__main__':
    port = 80
    print(f"Starting server on port {port}...")
    server = HTTPServer(('', port), HealthCheckHandler)
    server.serve_forever()
EOF

# Create systemd service
cat > /etc/systemd/system/app.service << 'EOF'
[Unit]
Description=Python Web App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/app
ExecStart=/usr/bin/python3 /opt/app/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable app
systemctl start app

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Application is running at:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "Health check:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/health"
echo ""
