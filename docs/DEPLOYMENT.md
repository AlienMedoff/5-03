# 🚀 Deployment Guide

## 📋 Overview

This guide covers deploying the Aether Multi-Agent Bot to production with full monitoring, security, and scalability.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx         │────│   Telegram Bot   │────│  AI Agent Hub   │
│   (Reverse      │    │   (FastAPI)      │    │  (Multi-model)  │
│    Proxy)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Prometheus    │────│   Redis Cache    │────│  AlertManager   │
│   (Metrics)     │    │   (Sessions)     │    │   (Alerts)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Grafana       │────│   Docker Host    │────│   Systemd       │
│   (Dashboards)  │    │   (Container)    │    │   (Auto-restart) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM:** 2GB minimum, 4GB recommended
- **CPU:** 2 cores minimum, 4 cores recommended
- **Storage:** 20GB minimum, 50GB recommended
- **Network:** Stable internet connection

### Software Requirements
- **Docker:** 20.10+
- **Docker Compose:** 2.0+
- **Git:** 2.25+
- **curl:** Latest version

### API Keys Required
- **Telegram Bot Token:** From @BotFather
- **Anthropic API Key:** Claude AI model
- **Mistral API Key:** Mistral AI model
- **Groq API Key:** Groq AI model
- **Google API Key:** Gemini AI model

## 🚀 Quick Deployment

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/aether-multi-agent-bot.git
cd aether-multi-agent-bot
```

### 2️⃣ Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3️⃣ Deploy
```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### 4️⃣ Verify Deployment
```bash
# Check service status
curl http://localhost:8080/health

# Check Docker containers
docker-compose ps
```

## 🔧 Manual Deployment

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Create project directory
sudo mkdir -p /opt/aether-multi-agent-bot
sudo chown $USER:$USER /opt/aether-multi-agent-bot
```

### Step 2: Application Setup
```bash
# Clone repository
cd /opt/aether-multi-agent-bot
git clone https://github.com/your-username/aether-multi-agent-bot.git .

# Configure environment
cp .env.example .env
nano .env

# Set permissions
chmod 600 .env
```

### Step 3: Deploy Services
```bash
# Build and start services
docker-compose up -d --build

# Wait for services to start
sleep 30

# Check health
docker-compose ps
curl http://localhost:8080/health
```

### Step 4: Setup Auto-restart
```bash
# Create systemd service
sudo tee /etc/systemd/system/aether-bot.service > /dev/null <<EOF
[Unit]
Description=Aether Multi-Agent Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/aether-multi-agent-bot
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable aether-bot.service
sudo systemctl start aether-bot.service
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8080/tcp  # Bot API
sudo ufw allow 3000/tcp  # Grafana
sudo ufw --force enable
```

### SSL/TLS Setup
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renew certificate
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Security Headers
```nginx
# Add to nginx.conf
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## 📊 Monitoring Setup

### Grafana Configuration
1. **Access Grafana:** http://localhost:3000
2. **Login:** admin / your GRAFANA_PASSWORD
3. **Add Prometheus datasource:**
   - URL: http://prometheus:9090
   - Access: Browser

### Key Dashboards
- **System Overview:** CPU, Memory, Disk usage
- **Bot Metrics:** Requests, Response time, Errors
- **AI Usage:** Model usage, Token consumption
- **Security Events:** Authentication, Rate limiting

### Alert Rules
```yaml
# monitoring/alerts.yml
groups:
  - name: bot_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(bot_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
      
      - alert: BotDown
        expr: up{job="bot"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Bot service is down"
```

## 🔧 Environment Variables

### Required Variables
```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABC...
ALERT_BOT_TOKEN=0987654321:XYZ...
ALERT_CHAT_ID=123456789
ALLOWED_USERS=123456789

# AI Model Keys
ANTHROPIC_API_KEY=sk-ant-...
MISTRAL_API_KEY=...
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...

# Security
SECRET_KEY=your-32-character-secret-key
REDIS_PASS=your-redis-password

# Monitoring
GRAFANA_PASSWORD=your-grafana-password
```

### Optional Variables
```bash
# Performance
RATE_LIMIT=10
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000

# Features
ENABLE_MONITORING=true
ENABLE_ALERTS=true
ENABLE_AUDIT=true

# Development
DEBUG=false
DEV_MODE=false
TEST_MODE=false
```

## 🔄 Maintenance

### Daily Tasks
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f bot

# Check metrics
curl http://localhost:8080/metrics
```

### Weekly Tasks
```bash
# Update application
cd /opt/aether-multi-agent-bot
git pull
docker-compose up -d --build

# Cleanup old images
docker image prune -f

# Check disk space
df -h
```

### Monthly Tasks
```bash
# Backup data
docker-compose exec redis redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /opt/backups/

# Update system
sudo apt update && sudo apt upgrade -y

# Review logs
grep ERROR /var/log/aether-bot/*.log
```

## 🆘 Troubleshooting

### Common Issues

#### Bot Not Starting
```bash
# Check logs
docker-compose logs bot

# Check environment
docker-compose exec bot env | grep TELEGRAM

# Verify token
curl -H "Authorization: Bearer $TELEGRAM_BOT_TOKEN" \
     https://api.telegram.org/bot$getMe
```

#### Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test connection
docker-compose exec bot python -c "
import redis
r = redis.Redis(host='redis', password='$REDIS_PASS')
print(r.ping())
"
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart

# Cleanup
docker system prune -f
```

#### Monitoring Issues
```bash
# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health

# Restart monitoring
docker-compose restart prometheus grafana
```

### Performance Optimization

#### Database Optimization
```bash
# Redis memory optimization
echo "maxmemory 256mb" >> docker/redis.conf
echo "maxmemory-policy allkeys-lru" >> docker/redis.conf
```

#### Application Optimization
```bash
# Increase worker processes
export WORKER_PROCESSES=8

# Enable caching
export ENABLE_CACHE=true

# Optimize rate limiting
export RATE_LIMIT=20
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  bot:
    scale: 3
    deploy:
      replicas: 3
```

### Load Balancing
```nginx
# nginx.conf
upstream bot_backend {
    server bot_1:8080;
    server bot_2:8080;
    server bot_3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://bot_backend;
    }
}
```

## 🔔 Notifications

### Telegram Alerts
```python
# Add to bot configuration
ALERT_WEBHOOK_URL=https://api.telegram.org/bot$ALERT_BOT_TOKEN/sendMessage
ALERT_CHAT_ID=your_chat_id
```

### Email Alerts
```bash
# Install postfix
sudo apt install postfix

# Configure alerts
echo "root@yourdomain.com" | sudo tee -a /etc/aliases
sudo newaliases
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)

## 🆘 Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify environment: `docker-compose exec bot env`
3. Test connectivity: `curl http://localhost:8080/health`
4. Review troubleshooting section above

For additional support, create an issue on GitHub.
