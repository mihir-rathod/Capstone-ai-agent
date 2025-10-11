#!/bin/bash

set -a
source .env
set +a

# Use MySQL config file
cat > /tmp/my.cnf <<EOF
[client]
host=${MYSQL_HOST}
user=${MYSQL_USER}
password=${MYSQL_PASSWORD}
EOF

mysql --defaults-extra-file=/tmp/my.cnf "${MYSQL_DATABASE}" -e "SELECT 1;"

rm /tmp/my.cnf