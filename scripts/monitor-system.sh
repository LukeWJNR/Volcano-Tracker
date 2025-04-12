#!/bin/bash
# System monitoring script for Volcano Dashboard production deployment
# This script checks system health and sends alerts if issues are detected

set -e

# Configuration - adjust these values as needed
CPU_THRESHOLD=80        # Alert if CPU usage is over 80%
MEMORY_THRESHOLD=80     # Alert if memory usage is over 80%
DISK_THRESHOLD=85       # Alert if disk usage is over 85%
APP_PORT=5000           # Application port to check
CHECK_INTERVAL=300      # Check every 5 minutes (300 seconds)
LOG_FILE="./logs/system_monitor.log"
ALERT_EMAIL="your-email@example.com"  # Change this to your email

# Create log directory if it doesn't exist
mkdir -p ./logs

# Function to send an alert
send_alert() {
    local subject="$1"
    local message="$2"
    
    echo "[$(date)] ALERT: $subject - $message" >> "$LOG_FILE"
    
    # Send email alert
    echo "$message" | mail -s "Volcano Dashboard Alert: $subject" "$ALERT_EMAIL"
    
    # You could also implement SMS alerts here using your Twilio integration
}

# Function to check CPU usage
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d. -f1)
    
    echo "[$(date)] CPU Usage: $cpu_usage%" >> "$LOG_FILE"
    
    if [ "$cpu_usage" -gt "$CPU_THRESHOLD" ]; then
        send_alert "High CPU Usage" "CPU usage is at $cpu_usage%, which exceeds the threshold of $CPU_THRESHOLD%."
        return 1
    fi
    
    return 0
}

# Function to check memory usage
check_memory() {
    local memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
    
    echo "[$(date)] Memory Usage: $memory_usage%" >> "$LOG_FILE"
    
    if [ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]; then
        send_alert "High Memory Usage" "Memory usage is at $memory_usage%, which exceeds the threshold of $MEMORY_THRESHOLD%."
        return 1
    fi
    
    return 0
}

# Function to check disk usage
check_disk() {
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    echo "[$(date)] Disk Usage: $disk_usage%" >> "$LOG_FILE"
    
    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        send_alert "High Disk Usage" "Disk usage is at $disk_usage%, which exceeds the threshold of $DISK_THRESHOLD%."
        return 1
    fi
    
    return 0
}

# Function to check if the application is running
check_application() {
    if ! curl -s http://localhost:$APP_PORT > /dev/null; then
        send_alert "Application Down" "The Volcano Dashboard application is not responding on port $APP_PORT."
        
        # Check Docker container status
        echo "[$(date)] Container Status:" >> "$LOG_FILE"
        docker-compose ps >> "$LOG_FILE" 2>&1
        
        # Check container logs
        echo "[$(date)] Container Logs (Last 20 lines):" >> "$LOG_FILE"
        docker-compose logs --tail=20 >> "$LOG_FILE" 2>&1
        
        return 1
    fi
    
    echo "[$(date)] Application Status: Running" >> "$LOG_FILE"
    return 0
}

# Function to check database connectivity
check_database() {
    # Load environment variables if available
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    if [ -z "$PGHOST" ] || [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ] || [ -z "$PGDATABASE" ]; then
        echo "[$(date)] Database Check: Skipped (missing credentials)" >> "$LOG_FILE"
        return 0
    fi
    
    if ! PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT 1" > /dev/null 2>&1; then
        send_alert "Database Connectivity Issue" "Cannot connect to the PostgreSQL database at $PGHOST."
        return 1
    fi
    
    echo "[$(date)] Database Status: Connected" >> "$LOG_FILE"
    return 0
}

# Main monitoring loop
echo "[$(date)] Starting system monitoring script" >> "$LOG_FILE"

while true; do
    echo "[$(date)] Running system checks..." >> "$LOG_FILE"
    
    check_cpu
    check_memory
    check_disk
    check_application
    check_database
    
    echo "[$(date)] Checks completed, sleeping for $CHECK_INTERVAL seconds" >> "$LOG_FILE"
    sleep "$CHECK_INTERVAL"
done