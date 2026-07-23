#!/usr/bin/env bash
set -euo pipefail

set -a
source .env
set +a

mkdir -p export

mongoexport --uri="$MONGODB_URI" --db=wonders_db --collection=wonders --jsonArray --out=export/wonders.json

echo "Export written to ./export/wonders.json"
