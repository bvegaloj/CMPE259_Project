#!/bin/bash
# Monitor custom evaluation progress

LOG_FILE="evaluation_custom_run.log"

if [ ! -f "$LOG_FILE" ]; then
 echo "Evaluation not started yet..."
 exit 1
fi

echo "CUSTOM EVALUATION PROGRESS"
echo "Watching: $LOG_FILE"
echo ""

# Count completed queries
USER_QUERIES=$(grep -c "User Query:" "$LOG_FILE" 2>/dev/null || echo 0)
TOTAL_QUERIES=40 # 20 for each model

echo "Progress:"
echo " Queries processed: $USER_QUERIES / $TOTAL_QUERIES"
echo ""

# Show last 40 lines
echo "Recent activity:"
tail -40 "$LOG_FILE"
echo ""
echo ""
echo "To watch live: tail -f $LOG_FILE"
