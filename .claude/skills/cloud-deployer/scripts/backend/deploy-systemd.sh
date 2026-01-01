#!/bin/bash
# Backend deployment using systemd service
# Usage: ./scripts/backend/deploy-systemd.sh [install|start|stop|restart|status]

set -e

ACTION=${1:-install}
SERVICE_NAME=${SERVICE_NAME:-todo-backend}
USER=${USER:-$(whoami)}
WORK_DIR=${WORK_DIR:-/opt/todo-backend}
VENV_DIR=${VENV_DIR:-$WORK_DIR/venv}
PYTHON_CMD=${PYTHON_CMD:-python3.13}

case "$ACTION" in
  install)
    echo "Installing systemd service..."

    # Create virtual environment
    sudo mkdir -p $WORK_DIR
    sudo chown -R $USER:$USER $WORK_DIR
    cd $WORK_DIR
    $PYTHON_CMD -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    pip install -r requirements.txt

    # Create systemd service file
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Todo Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin"
EnvironmentFile=$WORK_DIR/.env
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ${SERVICE_NAME}
    echo "Service installed. Start with: sudo systemctl start ${SERVICE_NAME}"
    ;;
  start)
    sudo systemctl start ${SERVICE_NAME}
    echo "Service started"
    ;;
  stop)
    sudo systemctl stop ${SERVICE_NAME}
    echo "Service stopped"
    ;;
  restart)
    sudo systemctl restart ${SERVICE_NAME}
    echo "Service restarted"
    ;;
  status)
    sudo systemctl status ${SERVICE_NAME}
    ;;
  logs)
    sudo journalctl -u ${SERVICE_NAME} -f
    ;;
  uninstall)
    sudo systemctl stop ${SERVICE_NAME}
    sudo systemctl disable ${SERVICE_NAME}
    sudo rm /etc/systemd/system/${SERVICE_NAME}.service
    sudo systemctl daemon-reload
    echo "Service uninstalled"
    ;;
  *)
    echo "Usage: $0 [install|start|stop|restart|status|logs|uninstall]"
    exit 1
    ;;
esac
