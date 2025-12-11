#!/bin/bash
# Monitor evaluation progress

LOG_FILE="evaluation_run_fixed.log"
if [ ! -f "$LOG_FILE" ]; then
 LOG_FILE="evaluation_run.log"
fi

if [ ! -f "$LOG_FILE" ]; then
 echo "Evaluation not started yet..."
 exit 1
fi

echo "EVALUATION PROGRESS MONITOR"
echo "Watching: $LOG_FILE"
echo ""

# Count completed queries
USER_QUERIES=$(grep -c "User Query:" "$LOG_FILE" 2>/dev/null || echo 0)
TOTAL_QUERIES=40 # 20 for each model

echo "Progress:"
echo " Queries processed: $USER_QUERIES / $TOTAL_QUERIES"
echo ""

# Show last 30 lines
echo "Recent activity:"
tail -30 "$LOG_FILE"
echo ""
echo ""
echo "To see full log: tail -f evaluation_run.log"
echo "To stop: pkill -f 'python evaluation/evaluator.py'"
