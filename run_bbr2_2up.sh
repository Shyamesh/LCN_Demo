#!/bin/bash

# Configuration
SERVER_IP=192.168.10.55
DURATION=120       # total duration in seconds
INTERVAL=1         # iperf3 reporting interval

# Define ports and flow IDs
declare -a PORTS=(5201 5202)
declare -a FLOW_IDS=(1 2)

# Start ss -tin logging in background for each flow
for i in "${!PORTS[@]}"; do
    FLOW_ID=${FLOW_IDS[$i]}
    SS_LOG="ss_bbr2_flow${FLOW_ID}.txt"

    (
        echo "ss -tin log for flow $FLOW_ID" > "$SS_LOG"
        for ((t=0; t<DURATION; t++)); do
            echo "==== Time: $t seconds ====" >> "$SS_LOG"
            ss -tin >> "$SS_LOG"
            sleep 1
        done
    ) &
done

# Start iperf3 flows (client-side) in parallel
for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    FLOW_ID=${FLOW_IDS[$i]}
    iperf3 -c "$SERVER_IP" -p "$PORT" -C bbr2 -t "$DURATION" -i "$INTERVAL" --json > "bbr2_flow${FLOW_ID}.json" &
done

# Wait for all background jobs to complete
wait
echo "✅ All flows and ss logs completed."
