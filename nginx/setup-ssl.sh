#!/bin/bash
# Script to set up SSL certificates with Let's Encrypt for Volcano Dashboard

set -e

# Function to display help
show_help() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -d, --domain DOMAIN      Domain name for the certificate (required)"
  echo "  -e, --email EMAIL        Email address for Let's Encrypt (required)"
  echo "  -h, --help               Display this help message"
  exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--domain)
      DOMAIN="$2"
      shift 2
      ;;
    -e|--email)
      EMAIL="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      ;;
  esac
done

# Check if required parameters are provided
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Error: Domain name and email address are required."
  show_help
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

echo "📋 Setting up SSL certificate for $DOMAIN..."

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
  echo "🔧 Installing certbot..."
  apt-get update
  apt-get install -y certbot python3-certbot-nginx
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
  echo "❌ Nginx is not installed. Please install Nginx first."
  exit 1
fi

# Get SSL certificate
echo "🔒 Getting SSL certificate from Let's Encrypt..."
certbot --nginx --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN" -d "www.$DOMAIN"

# Verify certificate
echo "✅ Verifying certificate..."
certbot certificates

# Set up auto-renewal
echo "🔄 Setting up automatic renewal..."
echo "0 0,12 * * * root python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q" > /etc/cron.d/certbot-renewal
chmod 644 /etc/cron.d/certbot-renewal

echo "✅ SSL certificate has been successfully set up for $DOMAIN!"
echo "🔄 Certificate will automatically renew before expiration."