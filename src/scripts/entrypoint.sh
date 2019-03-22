#!/usr/bin/env bash

set -o errexit
set -o pipefail
cmd="$@"

function postgres_ready(){
python << END
import sys
import psycopg2

try:
    dbname = 'postgres'
    user = 'postgres'
    password = 'postgres'
    host = 'postgres'
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=5432)
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."
exec $cmd
