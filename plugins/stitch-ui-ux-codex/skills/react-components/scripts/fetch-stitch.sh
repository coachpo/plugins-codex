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
# Modified 2026-08-05 for HTTPS-only retrieval, isolated curl configuration,
# fixed project-local output, symlink rejection, bounded streaming downloads,
# and durable atomic no-clobber publication.

set -euo pipefail

URL="${1:-}"
OUTPUT="${2:-}"
MAX_BYTES=33554432

if [[ -z "$URL" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 <mcp_download_url> <.stitch/designs/filename>" >&2
  exit 2
fi

if [[ "$URL" != https://* ]]; then
  echo "Refusing a non-HTTPS URL." >&2
  exit 2
fi

case "$OUTPUT" in
  .stitch/designs/*) OUTPUT_NAME="${OUTPUT#.stitch/designs/}" ;;
  *)
    echo "Output must be a direct child of .stitch/designs/." >&2
    exit 2
    ;;
esac

case "$OUTPUT_NAME" in
  ""|.|..|.*|*/*|*$'\n'*|*$'\r'*)
    echo "Output must be one non-hidden filename inside .stitch/designs/." >&2
    exit 2
    ;;
esac

PROJECT_ROOT="$(/bin/pwd -P)"

enter_output_directory() {
  local component="$1"
  local expected_path="$2"

  if [[ -L "$component" ]]; then
    echo "Refusing a symlink in the .stitch/designs path." >&2
    exit 2
  fi
  if [[ ! -e "$component" ]]; then
    mkdir -- "$component"
  fi
  if [[ ! -d "$component" || -L "$component" ]]; then
    echo ".stitch/designs ancestors must be real directories." >&2
    exit 2
  fi
  cd -- "$component"
  if [[ "$(/bin/pwd -P)" != "$expected_path" ]]; then
    echo ".stitch/designs resolves outside the current project." >&2
    exit 2
  fi
}

enter_output_directory .stitch "$PROJECT_ROOT/.stitch"
enter_output_directory designs "$PROJECT_ROOT/.stitch/designs"
EXPECTED_OUTPUT_DIRECTORY="$PROJECT_ROOT/.stitch/designs"

# All remaining paths are relative to the verified physical directory. If an
# ancestor is renamed concurrently, these operations stay on the opened inode.
if [[ -e "$OUTPUT_NAME" || -L "$OUTPUT_NAME" ]]; then
  echo "Refusing to overwrite an existing artifact: $OUTPUT" >&2
  exit 3
fi

umask 077
TEMP_FILE="$(mktemp .stitch-fetch.XXXXXX)"
cleanup() {
  if [[ -n "${TEMP_FILE:-}" && -e "$TEMP_FILE" ]]; then
    rm -f -- "$TEMP_FILE"
  fi
}
trap cleanup EXIT
trap 'exit 130' HUP INT TERM

fsync_file() {
  NODE_OPTIONS='' node -e '
    const fs = require("node:fs");
    const fd = fs.openSync(process.argv[1], fs.constants.O_RDONLY);
    try {
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
  ' "$1"
}

fsync_directory() {
  NODE_OPTIONS='' node -e '
    const fs = require("node:fs");
    let fd;
    try {
      fd = fs.openSync(process.argv[1], fs.constants.O_RDONLY);
      fs.fsyncSync(fd);
    } catch (error) {
      if (error && (error.code === "EINVAL" || error.code === "ENOTSUP")) {
        process.exitCode = 0;
      } else {
        console.error(`Unable to fsync artifact directory: ${error && error.code ? error.code : error}`);
        process.exitCode = 1;
      }
    } finally {
      if (fd !== undefined) {
        fs.closeSync(fd);
      }
    }
  ' "$1"
}

output_matches_download() {
  [[ -e "$OUTPUT_NAME" && ! -L "$OUTPUT_NAME" && "$OUTPUT_NAME" -ef "$TEMP_FILE" ]]
}

fail_mismatched_destination() {
  if [[ -e "$OUTPUT_NAME" || -L "$OUTPUT_NAME" ]]; then
    echo "Published destination does not match this download; a non-matching destination was preserved." >&2
  else
    echo "Published destination disappeared; nothing was removed." >&2
  fi
  exit 3
}

handle_changed_directory() {
  if output_matches_download; then
    if ! rm -f -- "$OUTPUT_NAME"; then
      echo ".stitch/designs changed during publication; this download could not be removed." >&2
      exit 1
    fi
    if ! fsync_directory .; then
      echo ".stitch/designs changed during publication; this download was removed, but rollback durability could not be confirmed." >&2
      exit 1
    fi
    echo ".stitch/designs changed during publication; this download was removed." >&2
  elif [[ -e "$OUTPUT_NAME" || -L "$OUTPUT_NAME" ]]; then
    echo ".stitch/designs changed during publication; a non-matching destination was preserved." >&2
  else
    echo ".stitch/designs changed during publication; no destination remained to remove." >&2
  fi
  exit 2
}

rollback_after_sync_failure() {
  if output_matches_download; then
    if ! rm -f -- "$OUTPUT_NAME"; then
      echo "Failed to sync the artifact directory, and this download could not be removed." >&2
      exit 1
    fi
    if ! fsync_directory .; then
      echo "Failed to sync the artifact directory; this download was removed, but rollback durability could not be confirmed." >&2
      exit 1
    fi
    echo "Failed to sync the artifact directory; this download was removed." >&2
  elif [[ -e "$OUTPUT_NAME" || -L "$OUTPUT_NAME" ]]; then
    echo "Failed to sync the artifact directory; a non-matching destination was preserved." >&2
  else
    echo "Failed to sync the artifact directory; no destination remained to remove." >&2
  fi
  exit 1
}

READ_LIMIT=$((MAX_BYTES + 1))
if ! curl --disable \
  --fail \
  --silent \
  --show-error \
  --location \
  --globoff \
  --proto '=https' \
  --proto-redir '=https' \
  --connect-timeout 10 \
  --max-time 180 \
  --max-filesize "$MAX_BYTES" \
  --compressed \
  "$URL" \
  --output - \
  | head -c "$READ_LIMIT" > "$TEMP_FILE"; then
  FILE_BYTES="$(wc -c < "$TEMP_FILE" | tr -d '[:space:]')"
  if [[ "$FILE_BYTES" -gt "$MAX_BYTES" ]]; then
    echo "Refusing a Stitch artifact larger than 32 MiB." >&2
  else
    echo "Failed to retrieve the Stitch artifact." >&2
  fi
  exit 1
fi

FILE_BYTES="$(wc -c < "$TEMP_FILE" | tr -d '[:space:]')"
if [[ "$FILE_BYTES" -eq 0 ]]; then
  echo "Refusing an empty Stitch artifact." >&2
  exit 1
fi
if [[ "$FILE_BYTES" -gt "$MAX_BYTES" ]]; then
  echo "Refusing a Stitch artifact larger than 32 MiB." >&2
  exit 1
fi

if ! fsync_file "$TEMP_FILE"; then
  echo "Failed to make the downloaded Stitch artifact durable." >&2
  exit 1
fi

# Detect an ancestor rename before publication. Relative operations remain
# pinned to the verified directory if a later swap follows this check.
if [[ "$(/bin/pwd -P)" != "$EXPECTED_OUTPUT_DIRECTORY" ]]; then
  echo ".stitch/designs changed during retrieval; nothing was published." >&2
  exit 2
fi

if ! ln -h -- "$TEMP_FILE" "$OUTPUT_NAME"; then
  echo "Refusing to overwrite an artifact created concurrently: $OUTPUT" >&2
  exit 3
fi

if ! output_matches_download; then
  fail_mismatched_destination
fi

if [[ "$(/bin/pwd -P)" != "$EXPECTED_OUTPUT_DIRECTORY" ]]; then
  handle_changed_directory
fi

if ! fsync_directory .; then
  rollback_after_sync_failure
fi

if [[ "$(/bin/pwd -P)" != "$EXPECTED_OUTPUT_DIRECTORY" ]]; then
  handle_changed_directory
fi

if ! output_matches_download; then
  fail_mismatched_destination
fi

echo "Retrieved Stitch artifact: $OUTPUT ($FILE_BYTES bytes)"
