#!/usr/bin/env bash
set -euo pipefail

set -a
source .env
set +a

mongodump --uri="$MONGODB_URI" --db=wonders_db --out=dump

echo "Dump written to ./dump/wonders_db"
