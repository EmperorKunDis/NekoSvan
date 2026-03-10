#!/bin/bash
# NekoSvan CRM - PostgreSQL Backup Script
# Usage: ./scripts/backup.sh

set -e  # Exit on error

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/nekosvan_backup_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup.log"
RETENTION_DAYS=7

# Database credentials (from environment or defaults)
DB_HOST="${DB_HOST:-nekosvan_db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-nekosvan}"
DB_USER="${DB_USER:-nekosvan}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Start backup
log "Starting backup of database: ${DB_NAME}"

# Perform pg_dump
if PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F plain \
    --no-owner \
    --no-acl \
    -f "${BACKUP_FILE}"; then
    
    # Compress the backup
    gzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Get file size
    FILE_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    
    log "Backup completed successfully: ${BACKUP_FILE} (${FILE_SIZE})"
else
    log "ERROR: Backup failed!"
    exit 1
fi

# Rotate old backups (delete files older than RETENTION_DAYS)
log "Rotating backups (keeping last ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "nekosvan_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
DELETED_COUNT=$(find "${BACKUP_DIR}" -name "nekosvan_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} | wc -l)

if [ "${DELETED_COUNT}" -gt 0 ]; then
    log "Deleted ${DELETED_COUNT} old backup(s)"
else
    log "No old backups to delete"
fi

# List current backups
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "nekosvan_backup_*.sql.gz" -type f | wc -l)
log "Current backup count: ${BACKUP_COUNT}"

log "Backup process completed"
