#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Namespace where the Odoo pods are running
NAMESPACE=${NAMESPACE:-default}

# Directory to store database backups
DATABASE_DUMP_DIR=${DATABASE_DUMP_DIR:-/backups/db}
API_SERVER=${API_SERVER:-https://kubernetes.default.svc}

# Create backup directory if it doesn't exist
mkdir -p ${DATABASE_DUMP_DIR}

# get pod name from env var of the job and list database name and host from pod config using curl
TOKEN=$(cat ${TOKEN_FILE})

POD_CONFIG=$(curl -s --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" \
  "${API_SERVER}/api/v1/namespaces/${NAMESPACE}/pods/${POD_NAME}")


ODOO_DATABASE_HOST=$(jq '.spec.containers[] |  select(.name == "odoo-pv") | .env[] | select(.name == "ODOO_DATABASE_HOST") | .value' <<< "$POD_CONFIG")
ODOO_DATABASE_NAME=$(jq '.spec.containers[] |  select(.name == "odoo-pv") | .env[] | select(.name == "ODOO_DATABASE_NAME") | .value' <<< "$POD_CONFIG")

# Perform the database backup
pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -F c -b -v -f ${DATABASE_DUMP_DIR}/${POD_NAME}_${DB_NAME}_$(date +%Y%m%d).backup
echo "Dump of database ${DB_NAME} from pod ${POD_NAME} completed successfully."