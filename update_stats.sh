#!/bin/bash

source ~/python_projects/webapps/ronnie_stats/venv/bin/activate
python3 ./update_database.py

LOG_FILE=/var/log/warzone_stats/warzone_stats_log.txt

DATE=$(date)

if [ -f "$LOG_FILE" ]; then
    echo "$DATE new data" >> "$LOG_FILE"
else
    echo "$DATE new data" > "$LOG_FILE"
fi

deactivate



