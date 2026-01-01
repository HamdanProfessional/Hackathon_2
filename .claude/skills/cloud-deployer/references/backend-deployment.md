# Backend Deployment Reference

## Systemd Service

### Overview
systemd is the init system for modern Linux distributions. Running FastAPI as a systemd service provides:
- Automatic startup on boot
- Automatic restarts on failure
- Integrated logging with journalctl
- Resource limits and security policies

### Service File

Location: `/etc/systemd/system/todo-backend.service`

```ini
[Unit]
Description=Todo Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/todo-backend
Environment="PATH=/opt/todo-backend/venv/bin:/usr/local/bin"
EnvironmentFile=/opt/todo-backend/.env
ExecStart=/opt/todo-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/todo-backend/logs

# Resource limits
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

### Installation

```bash
# Create directory
sudo mkdir -p /opt/todo-backend
sudo chown $USER:$USER /opt/todo-backend

# Copy application files
cp -r backend/* /opt/todo-backend/

# Create virtual environment
cd /opt/todo-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
cp .env /opt/todo-backend/.env
sudo chown root:root /opt/todo-backend/.env
sudo chmod 600 /opt/todo-backend/.env

# Install service
sudo cp todo-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable todo-backend
sudo systemctl start todo-backend
```

### Management Commands

```bash
# Start service
sudo systemctl start todo-backend

# Stop service
sudo systemctl stop todo-backend

# Restart service
sudo systemctl restart todo-backend

# Check status
sudo systemctl status todo-backend

# View logs (real-time)
sudo journalctl -u todo-backend -f

# View logs (last 100 lines)
sudo journalctl -u todo-backend -n 100

# View logs since today
sudo journalctl -u todo-backend --since today

# Enable/disable on boot
sudo systemctl enable todo-backend
sudo systemctl disable todo-backend
```

## PM2 Process Manager

### Overview
PM2 is a Node.js process manager that also works well for Python applications via PM2 Plus. It provides:
- Process management and monitoring
- Zero-downtime reloads
- Cluster mode for multi-core utilization
- Web-based monitoring dashboard
- Log management

### Installation

```bash
# Install PM2 globally
npm install -g pm2

# Install PM2 for Python
pip install pm2
```

### Ecosystem Configuration

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'todo-backend',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: '/opt/todo-backend',
    interpreter: 'none',
    env_file: '/opt/todo-backend/.env',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/log/pm2/todo-backend-error.log',
    out_file: '/var/log/pm2/todo-backend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    env: {
      NODE_ENV: 'production'
    }
  }]
};
```

### Cluster Mode (Multi-Core)

```javascript
module.exports = {
  apps: [{
    name: 'todo-backend',
    script: 'venv/bin/gunicorn',
    args: 'app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000',
    instances: 'max',  // Use all CPUs
    exec_mode: 'cluster'
  }]
};
```

### Management Commands

```bash
# Start application
pm2 start ecosystem.config.js

# Stop application
pm2 stop todo-backend

# Restart application
pm2 restart todo-backend

# Zero-downtime reload
pm2 reload todo-backend

# Delete from PM2
pm2 delete todo-backend

# Show status
pm2 status
pm2 describe todo-backend

# View logs
pm2 logs todo-backend
pm2 logs todo-backend --lines 100

# Monitor
pm2 monit

# Save process list
pm2 save

# Start on boot
pm2 startup
# Follow the instructions, then:
pm2 save
```

### Advanced Features

**Log rotation:**
```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

**Monitoring with PM2 Plus:**
```bash
pm2 link <secret_key> <public_key>
```

## Gunicorn + Uvicorn Workers

### Overview
Gunicorn with Uvicorn workers provides production-grade performance:
- Multiple worker processes
- Automatic worker management
- Graceful restarts
- Better resource utilization

### Installation

```bash
pip install gunicorn uvicorn[standard]
```

### Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Process naming
proc_name = "todo-backend"

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
daemon = False
pidfile = "/var/run/gunicorn/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
```

### Running with Gunicorn

```bash
# Direct command
gunicorn -c gunicorn.conf.py app.main:app

# With systemd
ExecStart=/opt/todo-backend/venv/bin/gunicorn -c gunicorn.conf.py app.main:app

# With PM2
script: 'venv/bin/gunicorn',
args: '-c gunicorn.conf.py app.main:app'
```

## Nginx Reverse Proxy

### Configuration

```nginx
upstream todo_backend {
    server 127.0.0.1:8000;
    # For multiple workers
    # server unix:/var/run/gunicorn/gunicorn.sock;
}

server {
    listen 80;
    server_name api.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Logging
    access_log /var/log/nginx/todo-backend-access.log;
    error_log /var/log/nginx/todo-backend-error.log;

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    # API endpoints
    location / {
        proxy_pass http://todo_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://todo_backend/health;
        access_log off;
    }

    # Static files (if any)
    location /static {
        alias /opt/todo-backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### WebSocket Support

```nginx
location /ws {
    proxy_pass http://todo_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

## Security Best Practices

1. **Run as non-root user**: Create dedicated user for service
2. **Secure environment file**: `chmod 600 .env`
3. **Use firewall**: Only allow necessary ports (80, 443, 22)
4. **Enable HTTPS**: Use Let's Encrypt for SSL certificates
5. **Rate limiting**: Configure Nginx or use FastAPI middleware
6. **Log rotation**: Prevent disk filling with logs
7. **Regular updates**: Keep system and dependencies updated
8. **Monitoring**: Use tools like Prometheus, Grafana, Sentry

## Troubleshooting

### Service won't start
```bash
# Check status
sudo systemctl status todo-backend
pm2 status

# Check logs
sudo journalctl -u todo-backend -n 50
pm2 logs todo-backend --lines 50

# Test manually
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Port already in use
```bash
# Find process
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process
sudo kill -9 <PID>
```

### Memory issues
```bash
# Check memory usage
free -h
ps aux | grep uvicorn

# Adjust limits in service file or PM2 config
```

### Permission errors
```bash
# Check file ownership
ls -la /opt/todo-backend

# Fix ownership
sudo chown -R www-data:www-data /opt/todo-backend
```
