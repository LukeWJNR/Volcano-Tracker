#!/bin/bash
# Script to backup the PostgreSQL database for Volcano Dashboard

set -e

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found. Please create it with database credentials."
  exit 1
fi

# Default backup directory
BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_RETENTION="${BACKUP_RETENTION:-7}"  # Days to keep backups

# Timestamp for the backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${PGDATABASE}_$TIMESTAMP.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)..."

# Perform database backup
PGPASSWORD="$PGPASSWORD" pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -F p | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
  echo "✅ Backup completed successfully: $BACKUP_FILE"
  echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
  echo "❌ Backup failed!"
  exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than $BACKUP_RETENTION days..."
find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +$BACKUP_RETENTION -delete

echo "Backup process completed at $(date)"