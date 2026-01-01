#!/bin/bash
# Backend deployment using PM2 process manager
# Usage: ./scripts/backend/deploy-pm2.sh [start|stop|restart|status|logs]

set -e

ACTION=${1:-start}
APP_NAME=${APP_NAME:-todo-backend}
WORK_DIR=${WORK_DIR:-$(pwd)}
PYTHON_CMD=${PYTHON_CMD:-python3.13}

case "$ACTION" in
  start)
    echo "Starting backend with PM2..."

    # Install dependencies if needed
    if [ ! -d "venv" ]; then
      $PYTHON_CMD -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      pip install pm2
    fi

    # Create PM2 ecosystem file if not exists
    cat > ecosystem.config.js <<EOF
module.exports = {
  apps: [{
    name: '${APP_NAME}',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: '${WORK_DIR}',
    interpreter: 'none',
    env_file: '${WORK_DIR}/.env',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

    # Start with PM2
    npx pm2 start ecosystem.config.js
    npx pm2 save
    echo "Backend started with PM2"
    npx pm2 status
    ;;
  stop)
    npx pm2 stop ${APP_NAME}
    echo "Backend stopped"
    ;;
  restart)
    npx pm2 restart ${APP_NAME}
    echo "Backend restarted"
    ;;
  reload)
    npx pm2 reload ${APP_NAME}
    echo "Backend reloaded (zero-downtime)"
    ;;
  status)
    npx pm2 status
    npx pm2 describe ${APP_NAME}
    ;;
  logs)
    npx pm2 logs ${APP_NAME}
    ;;
  monit)
    npx pm2 monit
    ;;
  delete)
    npx pm2 delete ${APP_NAME}
    npx pm2 save
    echo "Backend deleted from PM2"
    ;;
  *)
    echo "Usage: $0 [start|stop|restart|reload|status|logs|monit|delete]"
    exit 1
    ;;
esac
