#!/bin/bash
# filepath: preparation/ad_hoc/search_markdown.sh

DOCS_DIR="/d/work/gramener/anand_assignment/project1/tds_project1_automation_agent/data/docs"
OUTPUT_FILE="$DOCS_DIR/index.json"

# Create a temporary file for building the JSON
temp=$(mktemp)

echo "{" > "$temp"
first_entry=true

# Find all .md files inside DOCS_DIR
while IFS= read -r file; do
  # Compute relative path
  rel_path=$(realpath --relative-to="$DOCS_DIR" "$file")

  # Extract first H1 line (# with optional spaces) and remove the leading '#' and spaces
  title=$(grep -m 1 '^# ' "$file" | sed 's/^# *//')
  
  # If no title is found, skip this file
  if [ -z "$title" ]; then
    continue
  fi

  # Escape any double quotes in the title
  title=$(echo "$title" | sed 's/"/\\"/g')

  # Add comma separator for JSON if not the first entry
  if [ "$first_entry" = true ]; then
    first_entry=false
  else
    echo "," >> "$temp"
  fi
  
  # Append JSON entry
  echo "  \"${rel_path}\": \"${title}\"" >> "$temp"
done < <(find "$DOCS_DIR" -type f -name "*.md")

echo "" >> "$temp"
echo "}" >> "$temp"

# Move temporary file to OUTPUT_FILE
mv "$temp" "$OUTPUT_FILE"
echo "Index file created at $OUTPUT_FILE"