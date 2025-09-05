#!/bin/bash
# Raspberry Pi monitoring script for Card Collector

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
COMPOSE_FILE="docker-compose.pi.yml"
THRESHOLD_CPU=80
THRESHOLD_MEM=85
THRESHOLD_DISK=90
THRESHOLD_TEMP=70

# Get system information
get_system_info() {
    # CPU usage (5 second average)
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    MEM_INFO=$(free | grep '^Mem')
    MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
    MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
    MEM_USAGE=$(( MEM_USED * 100 / MEM_TOTAL ))
    
    # Disk usage
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    # Temperature
    if command -v vcgencmd &> /dev/null; then
        TEMP=$(vcgencmd measure_temp | cut -d= -f2 | cut -d"'" -f1)
    else
        TEMP="N/A"
    fi
    
    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | cut -d',' -f1)
    
    # Uptime
    UPTIME=$(uptime -p)
}

# Check Docker services
check_docker_services() {
    if [ -f "$COMPOSE_FILE" ]; then
        log_info "Docker Service Status:"
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            docker-compose -f "$COMPOSE_FILE" ps | grep -E "(Name|cards-)" | while read line; do
                if echo "$line" | grep -q "Up"; then
                    SERVICE=$(echo "$line" | awk '{print $1}')
                    log_success "$SERVICE is running"
                elif echo "$line" | grep -q "Exit"; then
                    SERVICE=$(echo "$line" | awk '{print $1}')
                    log_error "$SERVICE has exited"
                fi
            done
        else
            log_warning "No Docker services running"
        fi
    else
        log_info "Docker compose file not found - checking native services"
    fi
}

# Check native services
check_native_services() {
    # Check systemd services
    if systemctl is-active cardbot.service &>/dev/null; then
        log_success "cardbot.service is active"
    elif systemctl is-enabled cardbot.service &>/dev/null; then
        log_warning "cardbot.service is enabled but not active"
    fi
    
    if systemctl is-active cardweb.service &>/dev/null; then
        log_success "cardweb.service is active"
    elif systemctl is-enabled cardweb.service &>/dev/null; then
        log_warning "cardweb.service is enabled but not active"
    fi
    
    # Check manual processes
    if pgrep -f "python -m bot.main" > /dev/null; then
        log_success "Bot process is running"
    else
        log_warning "Bot process not found"
    fi
    
    if pgrep -f "python -m web.app" > /dev/null; then
        log_success "Web process is running"
    else
        log_warning "Web process not found"
    fi
}

# Check web service health
check_web_health() {
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if curl -s -o /dev/null -w "%{http_code}" "http://$LOCAL_IP:8080/api/health" | grep -q "200"; then
        log_success "Web service health check passed"
    else
        log_error "Web service health check failed"
    fi
}

# Check resource thresholds
check_thresholds() {
    log_info "Resource Threshold Checks:"
    
    # CPU check
    if (( $(echo "$CPU_USAGE > $THRESHOLD_CPU" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "CPU usage high: ${CPU_USAGE}% (threshold: ${THRESHOLD_CPU}%)"
    else
        log_success "CPU usage: ${CPU_USAGE}%"
    fi
    
    # Memory check
    if [ $MEM_USAGE -gt $THRESHOLD_MEM ]; then
        log_warning "Memory usage high: ${MEM_USAGE}% (threshold: ${THRESHOLD_MEM}%)"
    else
        log_success "Memory usage: ${MEM_USAGE}%"
    fi
    
    # Disk check
    if [ $DISK_USAGE -gt $THRESHOLD_DISK ]; then
        log_warning "Disk usage high: ${DISK_USAGE}% (threshold: ${THRESHOLD_DISK}%)"
    else
        log_success "Disk usage: ${DISK_USAGE}%"
    fi
    
    # Temperature check
    if [ "$TEMP" != "N/A" ] && (( $(echo "$TEMP > $THRESHOLD_TEMP" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "Temperature high: ${TEMP}°C (threshold: ${THRESHOLD_TEMP}°C)"
    elif [ "$TEMP" != "N/A" ]; then
        log_success "Temperature: ${TEMP}°C"
    fi
}

# Show system overview
show_overview() {
    clear
    echo "🥧 Raspberry Pi Card Collector Monitor"
    echo "======================================="
    echo
    
    # Pi model
    if [ -f /proc/device-tree/model ]; then
        echo "Model: $(cat /proc/device-tree/model)"
    fi
    
    # OS info
    echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $UPTIME"
    echo
    
    # System resources
    echo "📊 System Resources:"
    echo "-------------------"
    printf "%-12s %s\n" "CPU Usage:" "${CPU_USAGE}%"
    printf "%-12s %s/%s (%s%%)\n" "Memory:" "$(( MEM_USED / 1024 ))MB" "$(( MEM_TOTAL / 1024 ))MB" "$MEM_USAGE"
    printf "%-12s %s%%\n" "Disk Usage:" "$DISK_USAGE"
    printf "%-12s %s\n" "Temperature:" "${TEMP}°C"
    printf "%-12s %s\n" "Load Avg:" "$LOAD_AVG"
    echo
}

# Continuous monitoring mode
continuous_monitor() {
    log_info "Starting continuous monitoring (press Ctrl+C to stop)"
    echo
    
    while true; do
        get_system_info
        show_overview
        check_docker_services
        check_native_services
        check_web_health
        check_thresholds
        
        echo
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Next update in 30 seconds..."
        sleep 30
    done
}

# Quick status check
quick_status() {
    get_system_info
    show_overview
    check_thresholds
    echo
    check_docker_services
    check_native_services
    check_web_health
}

# Show logs with filtering
show_logs() {
    echo
    echo "Log Options:"
    echo "1) Docker logs (all services)"
    echo "2) Bot logs only"
    echo "3) Web logs only"
    echo "4) System resource logs"
    echo "5) Error logs only"
    read -p "Enter choice [1-5]: " -n 1 -r
    echo
    
    case $REPLY in
        1)
            if [ -f "$COMPOSE_FILE" ]; then
                docker-compose -f "$COMPOSE_FILE" logs --tail=50 -f
            else
                log_error "Docker compose file not found"
            fi
            ;;
        2)
            if systemctl is-active cardbot.service &>/dev/null; then
                journalctl -u cardbot.service -n 50 -f
            elif [ -f "bot.log" ]; then
                tail -f bot.log
            else
                log_error "Bot logs not found"
            fi
            ;;
        3)
            if systemctl is-active cardweb.service &>/dev/null; then
                journalctl -u cardweb.service -n 50 -f
            elif [ -f "web.log" ]; then
                tail -f web.log
            else
                log_error "Web logs not found"
            fi
            ;;
        4)
            # Show system resource usage over time
            watch -n 2 'echo "=== $(date) ==="; \
                        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk "{print \$2}")"; \
                        echo "Memory: $(free -h | grep "^Mem" | awk "{print \$3 \"/\" \$2}")"; \
                        echo "Disk: $(df -h / | tail -1 | awk "{print \$3 \"/\" \$2 \" (\" \$5 \")\")"); \
                        echo "Temp: $(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo \"N/A\")"'
            ;;
        5)
            # Show only error logs
            if [ -f "$COMPOSE_FILE" ]; then
                docker-compose -f "$COMPOSE_FILE" logs | grep -i error
            fi
            journalctl -u cardbot.service -u cardweb.service | grep -i error
            ;;
        *)
            log_error "Invalid choice"
            ;;
    esac
}

# Performance optimization suggestions
suggest_optimizations() {
    get_system_info
    
    echo "🔧 Performance Optimization Suggestions:"
    echo "========================================"
    
    # Memory suggestions
    if [ $MEM_USAGE -gt 80 ]; then
        echo "• High memory usage detected:"
        echo "  - Consider reducing Docker container memory limits"
        echo "  - Check for memory leaks in applications"
        echo "  - Restart services to free memory: sudo systemctl restart cardbot cardweb"
    fi
    
    # CPU suggestions
    if (( $(echo "$CPU_USAGE > 70" | bc -l 2>/dev/null || echo 0) )); then
        echo "• High CPU usage detected:"
        echo "  - Check for CPU-intensive processes: top"
        echo "  - Consider reducing Discord bot activity"
        echo "  - Verify no stuck processes: ps aux | grep python"
    fi
    
    # Disk suggestions
    if [ $DISK_USAGE -gt 80 ]; then
        echo "• High disk usage detected:"
        echo "  - Clean Docker images: docker system prune -a"
        echo "  - Clean log files: sudo journalctl --vacuum-time=7d"
        echo "  - Check large files: du -h / | sort -hr | head -20"
    fi
    
    # Temperature suggestions
    if [ "$TEMP" != "N/A" ] && (( $(echo "$TEMP > 65" | bc -l 2>/dev/null || echo 0) )); then
        echo "• High temperature detected:"
        echo "  - Ensure adequate ventilation"
        echo "  - Consider adding heatsinks or fan"
        echo "  - Check CPU governor: cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    fi
    
    echo
    echo "💡 General optimizations:"
    echo "• Enable hardware acceleration if available"
    echo "• Use SSD instead of SD card for better I/O"
    echo "• Set up log rotation to prevent disk fill"
    echo "• Monitor regularly with this script"
}

# Main menu
show_menu() {
    echo
    echo "🥧 Pi Monitor Options"
    echo "===================="
    echo "1) Quick status check"
    echo "2) Continuous monitoring"
    echo "3) View logs"
    echo "4) Performance suggestions"
    echo "5) Resource usage graph"
    echo "6) Exit"
    echo
}

# Main function
main() {
    if [ ! -f /proc/device-tree/model ]; then
        log_error "This script is for Raspberry Pi only"
        exit 1
    fi
    
    # Change to project directory if it exists
    if [ -d "/home/pi/card-collector" ]; then
        cd "/home/pi/card-collector"
    fi
    
    # Handle command line arguments
    case "${1:-}" in
        "status"|"")
            quick_status
            ;;
        "monitor")
            continuous_monitor
            ;;
        "logs")
            show_logs
            ;;
        "optimize")
            suggest_optimizations
            ;;
        "interactive")
            while true; do
                show_menu
                read -p "Enter choice [1-6]: " -n 1 -r
                echo
                
                case $REPLY in
                    1) quick_status ;;
                    2) continuous_monitor ;;
                    3) show_logs ;;
                    4) suggest_optimizations ;;
                    5) 
                        echo "Starting resource monitoring..."
                        htop
                        ;;
                    6) 
                        log_info "Goodbye!"
                        exit 0
                        ;;
                    *) log_error "Invalid choice" ;;
                esac
                
                echo
                read -p "Press Enter to continue..."
            done
            ;;
        *)
            echo "Usage: $0 [status|monitor|logs|optimize|interactive]"
            echo "  status      - Quick status check (default)"
            echo "  monitor     - Continuous monitoring"  
            echo "  logs        - View service logs"
            echo "  optimize    - Performance suggestions"
            echo "  interactive - Interactive menu"
            ;;
    esac
}

main "$@"