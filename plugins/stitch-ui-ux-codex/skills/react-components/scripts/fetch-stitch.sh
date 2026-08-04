#!/usr/bin/env bash
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modified 2026-07-19 for HTTPS-only retrieval, bounded destinations, and
# atomic no-overwrite writes in the Stitch UI/UX Codex plugin.

set -euo pipefail

URL="${1:-}"
OUTPUT="${2:-}"

if [[ -z "$URL" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 <mcp_download_url> <.stitch/designs/output_path>" >&2
  exit 2
fi

if [[ "$URL" != https://* ]]; then
  echo "Refusing a non-HTTPS URL." >&2
  exit 2
fi

case "$OUTPUT" in
  .stitch/designs/*|*/.stitch/designs/*) ;;
  *)
    echo "Output must be inside a .stitch/designs directory." >&2
    exit 2
    ;;
esac

if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite an existing artifact: $OUTPUT" >&2
  exit 3
fi

OUTPUT_DIR="$(dirname "$OUTPUT")"
mkdir -p "$OUTPUT_DIR"
TEMP_FILE="$(mktemp "$OUTPUT_DIR/.stitch-fetch.XXXXXX")"

cleanup() {
  rm -f "$TEMP_FILE"
}
trap cleanup EXIT

curl \
  --fail \
  --silent \
  --show-error \
  --location \
  --proto '=https' \
  --proto-redir '=https' \
  --connect-timeout 10 \
  --max-time 180 \
  --compressed \
  "$URL" \
  --output "$TEMP_FILE"

mv "$TEMP_FILE" "$OUTPUT"
trap - EXIT
echo "Retrieved Stitch artifact: $OUTPUT"
