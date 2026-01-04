#!/bin/bash
# =============================================================================
# User Data Script for Load Balanced Web Servers
# =============================================================================

set -e

HOSTNAME="${hostname}"
APP_PORT="${app_port}"

echo "=========================================="
echo "Setting up ${HOSTNAME}"
echo "=========================================="
echo ""

# Update system
echo "[1/9] Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git software-properties-common

# Install Python
echo "[2/9] Installing Python..."
apt-get install -y -qq python3 python3-pip python3-venv

# Install Nginx
echo "[3/9] Installing Nginx..."
apt-get install -y -qq nginx

# Configure UFW firewall
echo "[4/9] Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable

# Create application directory
echo "[5/9] Creating application..."
mkdir -p /opt/app
cd /opt/app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
EOF

pip install --quiet -r requirements.txt

# Create FastAPI application
cat > app.py << 'EOFAPP'
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import socket
import psycopg2
import redis
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Load Balanced Web App",
    description="Simple FastAPI app behind DigitalOcean Load Balancer",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Redis configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "decode_responses": True,
}

# Get hostname for identifying which server responded
HOSTNAME = socket.gethostname()

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Hello from Load Balanced Web App!",
        "server": HOSTNAME,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return JSONResponse(content={
        "status": "healthy",
        "server": HOSTNAME,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.get("/info")
async def info():
    """Get server and connection information"""
    db_status = "disconnected"
    redis_status = "disconnected"

    # Check database connection
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        db_version = cursor.fetchone()[0]
        db_status = "connected"
        conn.close()
    except Exception as e:
        db_version = str(e)

    # Check Redis connection
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        redis_status = "connected"
        redis_info = r.info()
    except Exception as e:
        redis_info = {"error": str(e)}

    return JSONResponse(content={
        "server": HOSTNAME,
        "database": {
            "status": db_status,
            "version": db_version if db_status == "connected" else None
        },
        "redis": {
            "status": redis_status,
            "info": redis_info if redis_status == "connected" else None
        },
        "timestamp": datetime.utcnow().isoformat()
    })

@app.get("/api/test")
async def test_db():
    """Test database connection and return sample data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create test table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                server VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert request log
        cursor.execute(
            "INSERT INTO requests (server) VALUES (%s) RETURNING id",
            (HOSTNAME,)
        )
        request_id = cursor.fetchone()[0]

        # Get request count
        cursor.execute("SELECT COUNT(*) FROM requests")
        count = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return JSONResponse(content={
            "message": "Database test successful",
            "request_id": request_id,
            "total_requests": count,
            "server": HOSTNAME
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/counter")
async def increment_counter():
    """Test Redis connection with a counter"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        count = r.incr("visits")
        return JSONResponse(content={
            "visits": count,
            "server": HOSTNAME
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOFAPP

# Create systemd service
cat > /etc/systemd/system/app.service << 'EOF'
[Unit]
Description=FastAPI Web Application
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/app
Environment="PATH=/opt/app/venv/bin"
EnvironmentFile=-/opt/app/.env
ExecStart=/opt/app/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create environment file
cat > /opt/app/.env << EOFENV
DB_HOST=${db_host}
DB_PORT=${db_port}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}
REDIS_HOST=${redis_host}
REDIS_PORT=${redis_port}
JWT_SECRET=${jwt_secret}
EOFENV

# Configure Nginx as reverse proxy
cat > /etc/nginx/sites-available/default << 'EOFNGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        access_log off;
    }
}
EOFNGINX

# Test Nginx configuration
nginx -t

# Enable and start services
echo "[6/9] Enabling and starting services..."
systemctl daemon-reload
systemctl enable app
systemctl enable nginx

# Start application
systemctl start app

# Restart Nginx
systemctl restart nginx

# Set hostname
echo "[7/9] Setting hostname..."
hostnamectl set-hostname ${HOSTNAME}
echo "${HOSTNAME}" > /etc/hostname

# Create info page
echo "[8/9] Creating info page..."
cat > /var/www/html/index.html << EOFHTML
<!DOCTYPE html>
<html>
<head>
    <title>Load Balanced Server</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #0069ff; }
        .info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Welcome to ${HOSTNAME}</h1>
    <div class="success">
        <strong>Status:</strong> Server is running and healthy
    </div>
    <div class="info">
        <p><strong>Server:</strong> ${HOSTNAME}</p>
        <p><strong>IP Address:</strong> $(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)</p>
        <p><strong>Time:</strong> $(date -u)</p>
    </div>
    <p>
        <a href="/health">Health Check</a> |
        <a href="/info">Server Info</a> |
        <a href="/api/test">Database Test</a> |
        <a href="/api/counter">Visit Counter</a>
    </p>
</body>
</html>
EOFHTML

# Security hardening
echo "[9/9] Security hardening..."
# Disable password authentication for SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Server: ${HOSTNAME}"
echo "Status: Running"
echo ""
echo "Application URLs:"
echo "  http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)/"
echo "  http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)/health"
echo ""
echo "Systemd services:"
echo "  sudo systemctl status app"
echo "  sudo systemctl status nginx"
echo ""
echo "Logs:"
echo "  sudo journalctl -u app -f"
echo "  sudo tail -f /var/log/nginx/access.log"
echo ""
