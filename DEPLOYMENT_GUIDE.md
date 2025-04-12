# Volcano Dashboard Deployment Guide

This guide provides step-by-step instructions for deploying the Volcano Monitoring Dashboard in a production environment using Docker. This containerized approach ensures security and prevents unauthorized code changes.

## Prerequisites

Before deploying, ensure you have:

- A Linux server with at least 2GB RAM and 1 CPU core
- Docker and Docker Compose installed
- Database credentials for PostgreSQL
- Twilio account for SMS alerts (if using early warning system)
- Root or sudo access to the server

## Step 1: Server Preparation

Update your server and install Docker if not already installed:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker

# Verify Docker is running
sudo docker --version
sudo docker-compose --version
```

## Step 2: Copy Application Files

1. Obtain the application files:
   - Download the zip file OR
   - Clone from version control

2. Create a directory for the application:
   ```bash
   sudo mkdir -p /opt/volcano-dashboard
   sudo chown -R $(whoami):$(whoami) /opt/volcano-dashboard
   ```

3. Extract or copy files to this directory:
   ```bash
   # If using zip file:
   unzip volcano-dashboard.zip -d /opt/volcano-dashboard
   
   # If using git:
   git clone <repository-url> /opt/volcano-dashboard
   ```

## Step 3: Configure Environment Variables

1. Navigate to the application directory:
   ```bash
   cd /opt/volcano-dashboard
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your credentials:
   ```bash
   nano .env
   ```
   
   Update all fields marked with `your_*_here` with your actual credentials.

## Step 4: Run the Deployment Script

Execute the deployment script:

```bash
sudo ./deploy.sh
```

The script will:
- Build the Docker container
- Configure permissions
- Start the application
- Verify it's running correctly

## Step 5: Verify Deployment

1. Check if the application is running:
   ```bash
   sudo docker-compose ps
   ```
   
   You should see the `app` container running.

2. Access the dashboard at `http://your-server-ip:5000`

## Troubleshooting

If the deployment fails:

1. Check logs:
   ```bash
   sudo docker-compose logs
   ```

2. Ensure all environment variables are set correctly in `.env`

3. Verify network connectivity to the database

4. Make sure ports are not blocked by firewall:
   ```bash
   sudo ufw allow 5000/tcp
   ```

## Updating the Application

When updates are available:

1. Navigate to the application directory:
   ```bash
   cd /opt/volcano-dashboard
   ```

2. Run the deployment script again:
   ```bash
   sudo ./deploy.sh
   ```

This will pull the latest code, rebuild the container, and restart the application.

## Security Measures

This deployment includes several security features:

- The application runs in a read-only container
- Environment variables are used for secrets
- The application runs as a non-root user
- Network access is limited to required ports only
- Data directories have strict permissions

For additional security, consider:

- Setting up SSL/TLS using a reverse proxy (Nginx/Apache)
- Implementing IP restrictions for admin pages
- Regular security updates for the host system