#!/usr/bin/env bash
set -euo pipefail

CSV_FILE="${1:-issues.csv}"

if [ ! -f "$CSV_FILE" ]; then
  echo "CSV file not found: $CSV_FILE"
  exit 1
fi

# Read CSV: title,body,labels,milestone
# Assumes no raw commas inside the fields; if you add them later,
# switch to a more robust CSV parser (python).
while IFS=, read -r title body labels milestone
do
  # Skip header
  if [ "$title" = "title" ]; then
    continue
  fi

  # Strip surrounding quotes from fields
  title="${title%\"}"
  title="${title#\"}"
  body="${body%\"}"
  body="${body#\"}"
  labels="${labels%\"}"
  labels="${labels#\"}"
  milestone="${milestone%\"}"
  milestone="${milestone#\"}"

  echo "Creating issue: $title"

  # Build label arguments from semicolon-separated list
  label_args=()
  IFS=';' read -ra parts <<< "$labels"
  for l in "${parts[@]}"; do
    # Trim whitespace
    l="$(echo "$l" | xargs)"
    if [ -n "$l" ]; then
      label_args+=( --label "$l" )
    fi
  done

  # Create issue via GitHub CLI
  gh issue create \
    --title "$title" \
    --body "$body" \
    "${label_args[@]}" \
    --milestone "$milestone"

done < "$CSV_FILE"
