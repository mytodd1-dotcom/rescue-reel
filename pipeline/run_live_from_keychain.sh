#!/usr/bin/env bash
set -euo pipefail

account="rescue-reel"

read_secret() {
  /usr/bin/security find-generic-password \
    -a "$account" \
    -s "$1" \
    -w
}

export GMI_API_KEY
export B2_KEY_ID
export B2_APP_KEY
export B2_BUCKET
export B2_REGION

GMI_API_KEY="$(read_secret rescue-reel-gmi-api-key)"
B2_KEY_ID="$(read_secret rescue-reel-b2-key-id)"
B2_APP_KEY="$(read_secret rescue-reel-b2-app-key)"
B2_BUCKET="$(read_secret rescue-reel-b2-bucket)"
B2_REGION="$(read_secret rescue-reel-b2-region)"

if [[ "$#" -eq 0 ]]; then
  exec .venv/bin/python pipeline/rescue_reel.py --live
fi

exec .venv/bin/python pipeline/rescue_reel.py "$@"
