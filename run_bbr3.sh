#!/bin/bash

# Configuration
SERVER_IP=192.168.10.45
DURATION=120       # total duration in seconds
INTERVAL=1         # iperf3 reporting interval

# Define port and flow ID
PORT=5202
FLOW_ID=1

# Start ss -tin logging in background
SS_LOG="ss_bbr3_flow${FLOW_ID}.txt"
(
    echo "ss -tin log for flow $FLOW_ID" > "$SS_LOG"
    for ((t=0; t<DURATION; t++)); do
        echo "==== Time: $t seconds ====" >> "$SS_LOG"
        ss -tin >> "$SS_LOG"
        sleep 1
    done
) &

# Start iperf3 flow (client-side) with BBR3
iperf3 -c "$SERVER_IP" -p "$PORT" -C bbr -t "$DURATION" -i "$INTERVAL" --json > "bbr3_flow${FLOW_ID}.json" &

# Wait for background jobs
wait
echo "✅ BBR3 flow and ss log completed."
