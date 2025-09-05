#!/bin/bash
# Raspberry Pi deployment script - quick deploy/update

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_DIR="/home/pi/card-collector"
COMPOSE_FILE="docker-compose.pi.yml"

# Check if we're on Pi and in the right directory
check_environment() {
    if [ ! -f /proc/device-tree/model ]; then
        log_error "This script is for Raspberry Pi only"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        log_info "Run setup_pi.sh first"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        log_info "Copy .env.example to .env and configure it"
        exit 1
    fi
}

# Update project from git
update_project() {
    log_info "Updating project from GitHub..."
    git pull origin master
    log_success "Project updated"
}

# Deploy using Docker
deploy_docker() {
    log_info "Deploying with Docker..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Pi Docker compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Stop existing services
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_info "Stopping existing services..."
        docker-compose -f "$COMPOSE_FILE" down
    fi
    
    # Build and start services
    log_info "Building and starting services..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Check service status
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_success "Docker services deployed successfully"
        
        # Show status
        echo
        log_info "Service Status:"
        docker-compose -f "$COMPOSE_FILE" ps
        
        echo
        log_info "Useful commands:"
        echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
        echo "  Stop services: docker-compose -f $COMPOSE_FILE down"
        echo "  Restart: docker-compose -f $COMPOSE_FILE restart"
        
    else
        log_error "Some services failed to start"
        docker-compose -f "$COMPOSE_FILE" ps
        docker-compose -f "$COMPOSE_FILE" logs
        exit 1
    fi
}

# Deploy using native Python
deploy_native() {
    log_info "Deploying with native Python..."
    
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        python3.11 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Update dependencies
    log_info "Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -e .
    
    # Check if systemd services exist
    if systemctl --user is-enabled cardbot.service &>/dev/null; then
        log_info "Restarting systemd services..."
        sudo systemctl restart cardbot cardweb
        sudo systemctl status cardbot cardweb --no-pager
    else
        log_info "Starting services manually..."
        log_warning "Consider setting up systemd services for auto-start"
        
        # Kill existing processes
        pkill -f "python -m bot.main" || true
        pkill -f "python -m web.app" || true
        
        # Start services in background
        nohup python -m web.app > web.log 2>&1 &
        nohup python -m bot.main > bot.log 2>&1 &
        
        sleep 3
        
        log_info "Services started in background"
        log_info "Check logs: tail -f web.log bot.log"
    fi
    
    log_success "Native deployment complete"
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # Check web service
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if curl -s "http://$LOCAL_IP:8080/api/health" > /dev/null; then
        log_success "Web service is responding"
    else
        log_warning "Web service not responding on http://$LOCAL_IP:8080"
    fi
    
    # Check system resources
    echo
    log_info "System Resources:"
    echo "Memory Usage: $(free -h | grep '^Mem' | awk '{print $3 "/" $2}')"
    echo "Disk Usage: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
    echo "CPU Temperature: $(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo 'N/A')"
    echo "Load Average: $(uptime | cut -d',' -f3- | sed 's/^ *//')"
}

# Show deployment options
show_menu() {
    echo
    echo "🥧 Raspberry Pi Deployment Options"
    echo "================================="
    echo "1) Update and deploy with Docker"
    echo "2) Update and deploy with native Python"
    echo "3) Health check only"
    echo "4) View logs"
    echo "5) Stop services"
    echo "6) Exit"
    echo
}

# View logs
view_logs() {
    echo
    echo "Choose log source:"
    echo "1) Docker logs"
    echo "2) Native logs" 
    echo "3) System logs"
    read -p "Enter choice [1-3]: " -n 1 -r
    echo
    
    case $REPLY in
        1)
            if [ -f "$COMPOSE_FILE" ]; then
                docker-compose -f "$COMPOSE_FILE" logs -f
            else
                log_error "Docker compose file not found"
            fi
            ;;
        2)
            if [ -f "bot.log" ] || [ -f "web.log" ]; then
                tail -f bot.log web.log
            else
                log_error "Native log files not found"
            fi
            ;;
        3)
            sudo journalctl -u cardbot -u cardweb -f
            ;;
        *)
            log_error "Invalid choice"
            ;;
    esac
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    # Stop Docker services
    if [ -f "$COMPOSE_FILE" ] && docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" down
        log_info "Docker services stopped"
    fi
    
    # Stop systemd services
    if systemctl --user is-enabled cardbot.service &>/dev/null; then
        sudo systemctl stop cardbot cardweb
        log_info "Systemd services stopped"
    fi
    
    # Stop manual processes
    pkill -f "python -m bot.main" || true
    pkill -f "python -m web.app" || true
    
    log_success "All services stopped"
}

# Main interactive menu
main() {
    check_environment
    
    while true; do
        show_menu
        read -p "Enter choice [1-6]: " -n 1 -r
        echo
        
        case $REPLY in
            1)
                update_project
                deploy_docker
                health_check
                ;;
            2)
                update_project
                deploy_native
                health_check
                ;;
            3)
                health_check
                ;;
            4)
                view_logs
                ;;
            5)
                stop_services
                ;;
            6)
                log_info "Goodbye!"
                exit 0
                ;;
            *)
                log_error "Invalid choice"
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Handle command line arguments
if [ $# -gt 0 ]; then
    check_environment
    case "$1" in
        "docker")
            update_project
            deploy_docker
            health_check
            ;;
        "native")
            update_project
            deploy_native
            health_check
            ;;
        "stop")
            stop_services
            ;;
        "health")
            health_check
            ;;
        "logs")
            view_logs
            ;;
        *)
            echo "Usage: $0 [docker|native|stop|health|logs]"
            exit 1
            ;;
    esac
else
    main
fi