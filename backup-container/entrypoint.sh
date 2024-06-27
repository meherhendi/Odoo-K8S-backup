#!/bin/bash

echo "Backup job started"
# backup database
./backup_db.sh
# backup odoo files
./backup.sh
# exit gracefully
echo "Odoo filestore and database backup was successful"
exit 0