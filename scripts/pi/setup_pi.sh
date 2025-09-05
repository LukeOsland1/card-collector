#!/bin/bash
# Raspberry Pi setup script for Card Collector Discord Bot

set -e

echo "🥧 Setting up Card Collector on Raspberry Pi"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if running on Raspberry Pi
check_pi() {
    if [ ! -f /proc/device-tree/model ]; then
        log_error "This script is designed for Raspberry Pi"
        exit 1
    fi
    
    PI_MODEL=$(cat /proc/device-tree/model)
    log_info "Detected: $PI_MODEL"
    
    # Check for 64-bit OS
    if [ "$(uname -m)" != "aarch64" ] && [ "$(uname -m)" != "arm64" ]; then
        log_warning "32-bit OS detected. 64-bit OS recommended for better performance"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Update system
update_system() {
    log_info "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
    log_success "System updated"
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker already installed"
        return
    fi
    
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Install Docker Compose
    sudo apt install docker-compose -y
    
    log_success "Docker installed"
    log_warning "Please logout and login again for Docker group changes to take effect"
}

# Install Python (fallback option)
install_python() {
    log_info "Installing Python development environment..."
    sudo apt install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        build-essential \
        libffi-dev \
        libssl-dev \
        git
    
    log_success "Python environment installed"
}

# Configure Pi optimizations
configure_pi() {
    log_info "Applying Raspberry Pi optimizations..."
    
    # Memory split configuration
    if ! grep -q "gpu_mem=128" /boot/config.txt; then
        echo "gpu_mem=128" | sudo tee -a /boot/config.txt
        log_info "Set GPU memory split to 128MB"
    fi
    
    # Enable memory cgroup
    if ! grep -q "cgroup_memory=1" /boot/cmdline.txt; then
        sudo sed -i '$ s/$/ cgroup_memory=1 cgroup_enable=memory/' /boot/cmdline.txt
        log_info "Enabled memory cgroups"
    fi
    
    # Increase file limits
    if ! grep -q "* soft nofile 65536" /etc/security/limits.conf; then
        echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
        echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
        log_info "Increased file descriptor limits"
    fi
    
    # Configure swap (if needed)
    TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
    if [ $TOTAL_MEM -lt 4000 ]; then
        log_info "Low memory detected ($TOTAL_MEM MB). Configuring swap..."
        sudo dphys-swapfile swapoff
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
        sudo dphys-swapfile setup
        sudo dphys-swapfile swapon
        log_success "Swap configured to 2GB"
    fi
    
    log_success "Pi optimizations applied"
}

# Setup project directory
setup_project() {
    log_info "Setting up project directory..."
    
    # Create data directory
    sudo mkdir -p /home/pi/card-collector-data
    sudo chown pi:pi /home/pi/card-collector-data
    
    # Check if project already exists
    if [ -d "/home/pi/card-collector" ]; then
        log_warning "Project directory already exists"
        read -p "Update existing installation? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd /home/pi/card-collector
            git pull origin master
        fi
    else
        log_info "Cloning project..."
        cd /home/pi
        git clone https://github.com/LukeOsland1/card-collector.git
        cd card-collector
    fi
    
    log_success "Project setup complete"
}

# Setup environment configuration
setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_info "Created .env file from template"
        log_warning "Please edit .env file with your Discord bot credentials"
        log_warning "Run: nano .env"
    else
        log_info ".env file already exists"
    fi
}

# Choose deployment method
choose_deployment() {
    echo
    echo "Choose deployment method:"
    echo "1) Docker (Recommended - easier setup)"
    echo "2) Native Python (Better performance)"
    read -p "Enter choice [1-2]: " -n 1 -r
    echo
    
    case $REPLY in
        1)
            deploy_docker
            ;;
        2)
            deploy_native
            ;;
        *)
            log_error "Invalid choice"
            choose_deployment
            ;;
    esac
}

# Docker deployment
deploy_docker() {
    log_info "Setting up Docker deployment..."
    
    if [ ! -f "docker-compose.pi.yml" ]; then
        log_error "docker-compose.pi.yml not found"
        exit 1
    fi
    
    # Build and start services
    docker-compose -f docker-compose.pi.yml build
    docker-compose -f docker-compose.pi.yml up -d
    
    log_success "Docker services started"
    log_info "Check status with: docker-compose -f docker-compose.pi.yml ps"
    log_info "View logs with: docker-compose -f docker-compose.pi.yml logs -f"
}

# Native Python deployment
deploy_native() {
    log_info "Setting up native Python deployment..."
    
    # Create virtual environment
    python3.11 -m venv .venv
    source .venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -e .
    
    log_success "Python environment ready"
    log_info "Activate with: source .venv/bin/activate"
    log_info "Run bot with: python -m bot.main"
    log_info "Run web with: python -m web.app"
}

# Setup systemd services for native deployment
setup_systemd_services() {
    if [ ! -d ".venv" ]; then
        log_warning "Virtual environment not found. Run native deployment first."
        return
    fi
    
    log_info "Setting up systemd services..."
    
    # Bot service
    sudo tee /etc/systemd/system/cardbot.service > /dev/null <<EOF
[Unit]
Description=Card Collector Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/card-collector
Environment=PATH=/home/pi/card-collector/.venv/bin
ExecStart=/home/pi/card-collector/.venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Web service
    sudo tee /etc/systemd/system/cardweb.service > /dev/null <<EOF
[Unit]
Description=Card Collector Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/card-collector
Environment=PATH=/home/pi/card-collector/.venv/bin
ExecStart=/home/pi/card-collector/.venv/bin/python -m web.app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable cardbot cardweb
    
    log_success "Systemd services created"
    log_info "Start with: sudo systemctl start cardbot cardweb"
    log_info "Check status: sudo systemctl status cardbot cardweb"
}

# Main installation process
main() {
    echo
    log_info "Starting Raspberry Pi setup for Card Collector..."
    
    check_pi
    update_system
    install_docker
    install_python
    configure_pi
    setup_project
    setup_environment
    
    echo
    log_success "Basic setup complete!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your Discord bot credentials: nano .env"
    echo "2. Choose deployment method"
    echo
    
    read -p "Continue with deployment setup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        choose_deployment
        
        echo
        read -p "Setup auto-start services? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            setup_systemd_services
        fi
    fi
    
    echo
    log_success "🎉 Raspberry Pi setup complete!"
    echo
    echo "Useful commands:"
    echo "  Docker: docker-compose -f docker-compose.pi.yml [up|down|logs]"
    echo "  Native: source .venv/bin/activate && python -m bot.main"
    echo "  Monitor: htop, iotop, docker stats"
    echo
    echo "Web interface will be available at: http://$(hostname -I | awk '{print $1}'):8080"
    echo
    
    if [ -f /boot/config.txt ]; then
        log_warning "A system reboot is recommended to apply all optimizations"
        read -p "Reboot now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo reboot
        fi
    fi
}

# Run main function
main "$@"