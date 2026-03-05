#!/bin/bash

# 🚀 Aether Multi-Agent Bot Deployment Script
# Production deployment with full monitoring and security

set -e  # Exit on any error

# 🎨 Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 📋 Configuration
PROJECT_NAME="aether-multi-agent-bot"
DOCKER_REGISTRY="your-registry.com"
SERVER_HOST="${SERVER_HOST:-localhost}"
SERVER_USER="${SERVER_USER:-ubuntu}"
REPO_URL="https://github.com/your-username/aether-multi-agent-bot.git"

# 📁 Directories
DEPLOY_DIR="/opt/${PROJECT_NAME}"
BACKUP_DIR="/opt/backups/${PROJECT_NAME}"
LOG_DIR="/var/log/${PROJECT_NAME}"

# 🎯 Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 🔍 Pre-deployment checks
check_prerequisites() {
    log_info "🔍 Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_error "❌ Don't run this script as root!"
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "❌ Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "❌ Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f .env ]]; then
        log_error "❌ .env file not found. Copy .env.example and configure it."
        exit 1
    fi
    
    # Check if required environment variables are set
    source .env
    
    required_vars=("TELEGRAM_BOT_TOKEN" "ALLOWED_USERS" "REDIS_PASS" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "❌ Required environment variable $var is not set"
            exit 1
        fi
    done
    
    log_success "✅ All prerequisites passed"
}

# 📁 Setup directories
setup_directories() {
    log_info "📁 Setting up directories..."
    
    # Create directories
    sudo mkdir -p "$DEPLOY_DIR" "$BACKUP_DIR" "$LOG_DIR"
    
    # Set permissions
    sudo chown -R "$USER:$USER" "$DEPLOY_DIR"
    sudo chown -R "$USER:$USER" "$BACKUP_DIR"
    sudo chown -R "$USER:$USER" "$LOG_DIR"
    
    log_success "✅ Directories created"
}

# 💾 Backup existing deployment
backup_existing() {
    if [[ -d "$DEPLOY_DIR" && -n "$(ls -A "$DEPLOY_DIR" 2>/dev/null)" ]]; then
        log_info "💾 Backing up existing deployment..."
        
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
        
        # Stop existing services
        cd "$DEPLOY_DIR" || exit 1
        docker-compose down || true
        
        # Backup data
        mkdir -p "$BACKUP_PATH"
        cp -r . "$BACKUP_PATH/"
        
        log_success "✅ Backup created: $BACKUP_PATH"
    else
        log_info "ℹ️ No existing deployment to backup"
    fi
}

# 📥 Clone or update repository
setup_repository() {
    log_info "📥 Setting up repository..."
    
    if [[ -d "$DEPLOY_DIR/.git" ]]; then
        log_info "📥 Updating existing repository..."
        cd "$DEPLOY_DIR" || exit 1
        git pull origin main
    else
        log_info "📥 Cloning repository..."
        git clone "$REPO_URL" "$DEPLOY_DIR"
        cd "$DEPLOY_DIR" || exit 1
    fi
    
    log_success "✅ Repository setup complete"
}

# 🔐 Setup environment
setup_environment() {
    log_info "🔐 Setting up environment..."
    
    # Copy .env file if not exists
    if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
        cp .env "$DEPLOY_DIR/.env"
    fi
    
    # Set proper permissions
    chmod 600 "$DEPLOY_DIR/.env"
    
    # Create logs directory
    mkdir -p "$DEPLOY_DIR/logs"
    
    log_success "✅ Environment setup complete"
}

# 🐳 Build and deploy Docker containers
deploy_containers() {
    log_info "🐳 Building and deploying containers..."
    
    cd "$DEPLOY_DIR" || exit 1
    
    # Build images
    log_info "🏗️ Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    log_info "🚀 Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "unhealthy\|exited"; then
        log_error "❌ Some services are not healthy"
        docker-compose logs
        exit 1
    fi
    
    log_success "✅ All services are running and healthy"
}

# 🧪 Run health checks
run_health_checks() {
    log_info "🏥 Running health checks..."
    
    # Check main service
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_success "✅ Main service is healthy"
    else
        log_error "❌ Main service is not responding"
        exit 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "✅ Redis is healthy"
    else
        log_error "❌ Redis is not responding"
        exit 1
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        log_success "✅ Prometheus is healthy"
    else
        log_warning "⚠️ Prometheus is not responding (may be starting up)"
    fi
    
    # Check Grafana
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        log_success "✅ Grafana is healthy"
    else
        log_warning "⚠️ Grafana is not responding (may be starting up)"
    fi
}

# 🔧 Setup monitoring
setup_monitoring() {
    log_info "📊 Setting up monitoring..."
    
    # Create systemd service for auto-restart
    sudo tee /etc/systemd/system/aether-bot.service > /dev/null <<EOF
[Unit]
Description=Aether Multi-Agent Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable service
    sudo systemctl daemon-reload
    sudo systemctl enable aether-bot.service
    
    log_success "✅ Monitoring setup complete"
}

# 🔒 Setup security
setup_security() {
    log_info "🔒 Setting up security..."
    
    # Setup firewall rules
    if command -v ufw &> /dev/null; then
        sudo ufw allow 22/tcp    # SSH
        sudo ufw allow 8080/tcp  # Bot API
        sudo ufw allow 3000/tcp  # Grafana
        sudo ufw --force enable
        log_success "✅ Firewall configured"
    fi
    
    # Setup log rotation
    sudo tee /etc/logrotate.d/aether-bot > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -C $DEPLOY_DIR restart bot
    endscript
}
EOF
    
    log_success "✅ Security setup complete"
}

# 📊 Show deployment status
show_status() {
    log_info "📊 Deployment status:"
    echo ""
    
    echo "🐳 Docker containers:"
    docker-compose ps
    echo ""
    
    echo "📊 Service URLs:"
    echo "  • Bot API: http://localhost:8080"
    echo "  • Health: http://localhost:8080/health"
    echo "  • Metrics: http://localhost:8080/metrics"
    echo "  • Grafana: http://localhost:3000 (admin/GRAFANA_PASSWORD)"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    
    echo "📁 Important paths:"
    echo "  • Deployment: $DEPLOY_DIR"
    echo "  • Logs: $LOG_DIR"
    echo "  • Backups: $BACKUP_DIR"
    echo ""
    
    echo "🔧 Useful commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Restart: docker-compose restart"
    echo "  • Stop: docker-compose down"
    echo "  • Update: cd $DEPLOY_DIR && git pull && docker-compose up -d --build"
}

# 🧹 Cleanup function
cleanup() {
    if [[ $? -ne 0 ]]; then
        log_error "❌ Deployment failed. Cleaning up..."
        cd "$DEPLOY_DIR" 2>/dev/null || true
        docker-compose down || true
        exit 1
    fi
}

# 🎯 Main deployment function
main() {
    log_info "🚀 Starting Aether Multi-Agent Bot deployment..."
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    setup_directories
    backup_existing
    setup_repository
    setup_environment
    deploy_containers
    run_health_checks
    setup_monitoring
    setup_security
    show_status
    
    log_success "🎉 Deployment completed successfully!"
    log_info "🤖 Your Aether Multi-Agent Bot is now running!"
}

# 🚀 Run deployment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
