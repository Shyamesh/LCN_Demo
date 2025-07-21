# #!/bin/bash

# SERVER_IP="192.168.10.55"
# DURATION=10  # Duration of test in seconds
# INTERVAL=1
# PORT_CUBIC=5201

# CUBIC_JSON="cubic_results.json"
# CUBIC_STDOUT="cubic_stdout.txt"
# CUBIC_SS_TXT="cubic_ss.txt"

# # Function to capture ss -tin output every second
# function capture_ss() {
#   local fname=$1
#   for ((i=0; i<$DURATION; i++)); do
#     echo "=== $(date '+%T') ===" >> "$fname"
#     ss -tin >> "$fname"
#     echo -e "\n" >> "$fname"
#     sleep 1
#   done
# }

# # Start capturing ss in background
# echo "Capturing TCP metrics with ss -tin..."
# capture_ss "$CUBIC_SS_TXT" &
# capture_pid=$!

# # Start iperf3 CUBIC flow
# echo "Running iperf3 CUBIC client..."
# iperf3 -c "$SERVER_IP" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J -R > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
# iperf_pid=$!

# # Wait for both background jobs to finish
# wait "$iperf_pid"
# wait "$capture_pid"

# echo "CUBIC test complete."
# echo "Files generated:"
# echo " - iperf3 JSON:     $CUBIC_JSON"
# echo " - iperf3 stderr:   $CUBIC_STDOUT"
# echo " - ss -tin output:  $CUBIC_SS_TXT"





#!/bin/bash

# Configuration
SERVER_IP=192.168.10.45
DURATION=120       # total duration in seconds
INTERVAL=1         # iperf3 reporting interval

# Define port and flow ID
PORT=5201
FLOW_ID=1

# Start ss -tin logging in background
SS_LOG="ss_cubic_flow${FLOW_ID}.txt"
(
    echo "ss -tin log for flow $FLOW_ID" > "$SS_LOG"
    for ((t=0; t<DURATION; t++)); do
        echo "==== Time: $t seconds ====" >> "$SS_LOG"
        ss -tin >> "$SS_LOG"
        sleep 1
    done
) &

# Start iperf3 flow (client-side) with CUBIC
iperf3 -c "$SERVER_IP" -p "$PORT" -C cubic -t "$DURATION" -i "$INTERVAL" --json -R > "cubic_flow${FLOW_ID}.json" &

# Wait for background jobs
wait
echo "✅ CUBIC flow and ss log completed."
