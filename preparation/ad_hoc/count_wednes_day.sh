#!/bin/sh

count=0

while IFS= read -r date_str; do
  day_of_week=$(date -d "$date_str" +"%w")
  if [ "$day_of_week" -eq 3 ]; then
    count=$((count + 1))
  fi
done < ../../data/dates.txt

echo "$count" > ../../data/dates-wednesdays.txt