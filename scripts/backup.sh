#!/bin/bash

# Arthachitra Backup Script

set -e

BACKUP_DIR="/var/backups/arthachitra"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Database configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="arthachitra"
DB_USER="postgres"
DB_PASSWORD="password"

# S3 configuration (optional)
S3_BUCKET="arthachitra-backups"
AWS_REGION="ap-south-1"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

create_backup_dir() {
    log "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/uploads"
    mkdir -p "$BACKUP_DIR/config"
}

backup_database() {
    log "Backing up PostgreSQL database..."
    
    local backup_file="$BACKUP_DIR/database/arthachitra_${TIMESTAMP}.sql"
    
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-owner \
        --no-privileges \
        > "$backup_file"
    
    # Compress the backup
    gzip "$backup_file"
    log "Database backup completed: ${backup_file}.gz"
    
    # Verify backup
    if [ -f "${backup_file}.gz" ]; then
        log "✅ Database backup verified"
    else
        log "❌ Database backup failed"
        exit 1
    fi
}

backup_redis() {
    log "Backing up Redis data..."
    
    local backup_file="$BACKUP_DIR/redis_${TIMESTAMP}.rdb"
    
    # Get Redis data file
    docker exec arthachitra-redis-1 redis-cli --rdb /data/dump.rdb > /dev/null
    docker cp arthachitra-redis-1:/data/dump.rdb "$backup_file"
    
    if [ -f "$backup_file" ]; then
        gzip "$backup_file"
        log "✅ Redis backup completed: ${backup_file}.gz"
    else
        log "❌ Redis backup failed"
    fi
}

backup_uploads() {
    log "Backing up user uploads..."
    
    local uploads_dir="./uploads"
    local backup_file="$BACKUP_DIR/uploads/uploads_${TIMESTAMP}.tar.gz"
    
    if [ -d "$uploads_dir" ]; then
        tar -czf "$backup_file" -C "$uploads_dir" .
        log "✅ Uploads backup completed: $backup_file"
    else
        log "ℹ️ No uploads directory found"
    fi
}

backup_config() {
    log "Backing up configuration files..."
    
    local config_backup="$BACKUP_DIR/config/config_${TIMESTAMP}.tar.gz"
    
    tar -czf "$config_backup" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        ./config \
        ./docker-compose.yml \
        ./docker-compose.prod.yml \
        2>/dev/null || true
    
    log "✅ Configuration backup completed: $config_backup"
}

upload_to_s3() {
    if command -v aws > /dev/null 2>&1 && [ -n "$S3_BUCKET" ]; then
        log "Uploading backups to S3..."
        
        aws s3 sync "$BACKUP_DIR" "s3://$S3_BUCKET/backups/$TIMESTAMP/" \
            --region "$AWS_REGION" \
            --storage-class STANDARD_IA
        
        log "✅ Backups uploaded to S3"
    else
        log "ℹ️ S3 upload skipped (AWS CLI not available or S3_BUCKET not set)"
    fi
}

cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # Remove local backups older than retention period
    find "$BACKUP_DIR" -type f -mtime +"$RETENTION_DAYS" -delete
    
    # Remove empty directories
    find "$BACKUP_DIR" -type d -empty -delete
    
    # Clean up old S3 backups if AWS CLI is available
    if command -v aws > /dev/null 2>&1 && [ -n "$S3_BUCKET" ]; then
        cutoff_date=$(date -d "$RETENTION_DAYS days ago" "+%Y-%m-%d")
        aws s3api list-objects-v2 --bucket "$S3_BUCKET" --prefix "backups/" \
            --query "Contents[?LastModified<'$cutoff_date'][].Key" \
            --output text | xargs -I {} aws s3 rm "s3://$S3_BUCKET/{}"
    fi
    
    log "✅ Old backups cleaned up"
}

verify_backup_integrity() {
    log "Verifying backup integrity..."
    
    # Check database backup
    local db_backup="$BACKUP_DIR/database/arthachitra_${TIMESTAMP}.sql.gz"
    if [ -f "$db_backup" ]; then
        if zcat "$db_backup" | head -n 1 | grep -q "PostgreSQL database dump"; then
            log "✅ Database backup integrity verified"
        else
            log "❌ Database backup integrity check failed"
            exit 1
        fi
    fi
    
    log "✅ Backup integrity verification completed"
}

main() {
    log "Starting Arthachitra backup process..."
    
    create_backup_dir
    backup_database
    backup_redis
    backup_uploads
    backup_config
    verify_backup_integrity
    upload_to_s3
    cleanup_old_backups
    
    log "✅ Backup process completed successfully!"
    log "Backup location: $BACKUP_DIR"
    
    # Display backup size
    backup_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "Total backup size: $backup_size"
}

# Run main function
main "$@"
