#!/bin/bash

# Check if date argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 YYYY-MM-DD"
  exit 1
fi

DATE=$1
DB_CONTAINER="medium-db"
DB_USER="medium_user"
DB_NAME="medium_db"
# Assuming script is run from project root, or we can use absolute path or relative to script location
# Let's assume project root for simplicity as requested "./scripts/..."
PROCESSED_DIR="./processed"

# Delete from DB
echo "Deleting articles for date $DATE from database..."
if docker ps | grep -q $DB_CONTAINER; then
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "DELETE FROM articles WHERE publication_date = '$DATE';"
else
    echo "Error: Container $DB_CONTAINER is not running."
    exit 1
fi

# Delete file
FILE="$PROCESSED_DIR/medium-$DATE.sql"
if [ -f "$FILE" ]; then
  echo "Deleting processed file $FILE..."
  rm "$FILE"
else
  echo "File $FILE not found in $PROCESSED_DIR."
fi

echo "Operation completed for date $DATE."
