#!/bin/bash

# URL for Factbase Trump Truth Social page
URL="https://factbase.app/t/donald-trump/truth-social"

# Fetch the page with curl, using a user-agent to mimic a browser
HTML=$(curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" "$URL")

if [ -z "$HTML" ]; then
    echo "Error: Failed to fetch page with curl."
    exit 1
fi

# Current time in PDT (system time from context: March 27, 2026, 06:56 AM PDT)
CURRENT_TIME=$(date -d "2026-03-27 06:56:00" +%s)  # Using provided system time for threshold calculation
THRESHOLD_TIME=$((CURRENT_TIME - 1800))  # 30 minutes ago in seconds

# Extract post timestamps and content from HTML (simplified parsing)
# This uses grep and awk to find timestamps and nearby content; adjust based on actual HTML structure
# Example: looking for timestamps in format like "Mar 27, 2026 06:45 AM PDT"
echo "Parsing HTML for posts..."

# Use a simple pattern to find timestamps and content (this may need refinement)
POSTS=$(echo "$HTML" | grep -o -E '<time[^>]*>[^<]*</time>|<span class="[^"]*time[^"]*">[^<]*</span>' | head -20)

if [ -z "$POSTS" ]; then
    echo "No post timestamps found in HTML."
    echo "NO_NEW_POSTS"
    exit 0
fi

NEW_POSTS=0
while IFS= read -r line; do
    # Extract timestamp text (crude extraction for demo)
    TIMESTAMP_TEXT=$(echo "$line" | sed -n 's/.*>\s*\([^<]*\)\s*<.*/\1/p')
    if [ -z "$TIMESTAMP_TEXT" ]; then
        continue
    fi
    
    # Convert timestamp to seconds (assuming format "Mar 27, 2026 06:45 AM PDT")
    POST_TIME=$(date -d "$TIMESTAMP_TEXT" +%s 2>/dev/null)
    if [ -z "$POST_TIME" ]; then
        continue
    fi
    
    # Check if within last 30 minutes
    if [ "$POST_TIME" -gt "$THRESHOLD_TIME" ]; then
        # Extract content near the timestamp (simplified: next <p> or <div>)
        CONTENT=$(echo "$HTML" | grep -A 5 "$TIMESTAMP_TEXT" | grep -o -E '<p[^>]*>[^<]*</p>|<div class="[^"]*content[^"]*">[^<]*</div>' | head -1 | sed 's/<[^>]*>//g')
        if [ -z "$CONTENT" ]; then
            CONTENT="No content found"
        fi
        
        TOPIC_SUMMARY="${CONTENT:0:50}..."
        if [ ${#CONTENT} -le 50 ]; then
            TOPIC_SUMMARY="$CONTENT"
        fi
        
        echo "NEW_POST: $TIMESTAMP_TEXT|$TOPIC_SUMMARY|$CONTENT"
        NEW_POSTS=$((NEW_POSTS + 1))
    fi
done <<< "$POSTS"

if [ "$NEW_POSTS" -eq 0 ]; then
    echo "NO_NEW_POSTS"
fi