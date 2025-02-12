#!/bin/bash

# Find the 10 most recent .log files, sorted by modification time (newest first)
find ../../data/logs/ -name "*.log" -type f -printf "%T@ %p\n" | sort -nr | head -n 10 | cut -d' ' -f2 > recent_logs.txt

# Loop through the recent log files and extract the first line
for log_file in $(cat recent_logs.txt); do
  head -n 1 "$log_file" >> ../../data/logs-recent.txt
done

# Remove the temporary file
rm recent_logs.txt