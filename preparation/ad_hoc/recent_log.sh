#!/bin/bash

# Define log directory
LOG_DIR="D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\logs"

# Define output file
OUTPUT_FILE="D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\logs-recent.txt"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Clear the output file before writing
> "$OUTPUT_FILE"

# Loop through log-0.log to log-9.log in order
for i in {0..9}; do
  log_file="$LOG_DIR/log-$i.log"
  
  # Check if the file exists before processing
  if [[ -f "$log_file" ]]; then
    head -n 1 "$log_file" >> "$OUTPUT_FILE"
  else
    echo "Warning: $log_file not found, skipping."
  fi
done