#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if RESTIC_REPOSITORY, RESTIC_PASSWORD, and RESTIC_BACKUP_PATH are set
if [[ -z "${RESTIC_REPOSITORY}" || -z "${RESTIC_PASSWORD}" || -z "${RESTIC_BACKUP_PATH}" ]]; then
  echo "Error: RESTIC_REPOSITORY, RESTIC_PASSWORD, and RESTIC_BACKUP_PATH must be set."
  exit 1
fi

# Initialize restic repository if it doesn't exist
if ! restic snapshots > /dev/null 2>&1; then
  echo "Initializing restic repository..."
  restic init
fi

echo "copying ODOO data..."
cp -r ${ODOO_DATA_DIR} ${RESTIC_BACKUP_PATH}
# Perform the backup
echo "Starting backup of ${RESTIC_BACKUP_PATH} ..."
restic backup ${RESTIC_BACKUP_PATH}

# Optional: Forget old backups and keep the last 7 daily, 4 weekly, and 12 monthly snapshots
echo "Deleting old backups..."
#TODO: make this configurable through env variables
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune

echo "Odoo filestore files backup completed successfully."
