# #!/bin/bash

# SERVER_IP="192.168.10.55"
# DURATION=120  # Duration in seconds
# INTERVAL=1

# PORT_CUBIC=5201
# PORT_BBR=5202

# # Output files
# CUBIC_JSON="cubic_results.json"
# CUBIC_STDOUT="cubic_stdout.txt"
# CUBIC_SS_TXT="cubic_ss.txt"

# BBR_JSON="bbr_results.json"
# BBR_STDOUT="bbr_stdout.txt"
# BBR_SS_TXT="bbr_ss.txt"

# # Function to capture TCP socket stats
# function capture_ss() {
#   local fname=$1
#   for ((i=0; i<$DURATION; i++)); do
#     echo "=== $(date '+%T') ===" >> "$fname"
#     ss -tin >> "$fname"
#     echo -e "\n" >> "$fname"
#     sleep 1
#   done
# }

# # Start CUBIC flow
# echo "Starting CUBIC flow..."
# capture_ss "$CUBIC_SS_TXT" &
# capture_cubic_pid=$!
# iperf3 -c "$SERVER_IP" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
# cubic_pid=$!

# # Start BBR flow
# echo "Starting BBR flow..."
# capture_ss "$BBR_SS_TXT" &
# capture_bbr_pid=$!
# iperf3 -c "$SERVER_IP" -p "$PORT_BBR" -C bbr -t "$DURATION" -i "$INTERVAL" -J > "$BBR_JSON" 2> "$BBR_STDOUT" &
# bbr_pid=$!

# # Wait for both flows to finish
# wait "$cubic_pid"
# wait "$bbr_pid"
# wait "$capture_cubic_pid"
# wait "$capture_bbr_pid"

# echo "Done. Files saved:"
# echo "CUBIC -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
# echo "BBR  -> $BBR_JSON, $BBR_STDOUT, $BBR_SS_TXT"



#!/bin/bash

# IP addresses of two servers
SERVER_IP1="192.168.10.55"  # for CUBIC
SERVER_IP2="192.168.10.45"  # for BBR

DURATION=120  # Duration in seconds
INTERVAL=1

PORT_CUBIC=5201
PORT_BBR=5202

# Output files
CUBIC_JSON="cubic_results.json"
CUBIC_STDOUT="cubic_stdout.txt"
CUBIC_SS_TXT="cubic_ss.txt"

BBR_JSON="bbr_results.json"
BBR_STDOUT="bbr_stdout.txt"
BBR_SS_TXT="bbr_ss.txt"

# Function to capture TCP socket stats filtered by IP and port
function capture_ss() {
  local fname=$1
  local ip=$2
  local port=$3
  for ((i=0; i<$DURATION; i++)); do
    echo "=== $(date '+%T') ===" >> "$fname"
    ss -tin | grep "$ip:$port" -A 10 >> "$fname"
    echo -e "\n" >> "$fname"
    sleep 1
  done
}

# Start CUBIC flow
echo "Starting CUBIC flow to $SERVER_IP1..."
capture_ss "$CUBIC_SS_TXT" "$SERVER_IP1" "$PORT_CUBIC" &
capture_cubic_pid=$!
iperf3 -c "$SERVER_IP1" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
cubic_pid=$!

# Start BBR flow
echo "Starting BBR flow to $SERVER_IP2..."
capture_ss "$BBR_SS_TXT" "$SERVER_IP2" "$PORT_BBR" &
capture_bbr_pid=$!
iperf3 -c "$SERVER_IP2" -p "$PORT_BBR" -C bbr -t "$DURATION" -i "$INTERVAL" -J > "$BBR_JSON" 2> "$BBR_STDOUT" &
bbr_pid=$!

# Wait for both flows and capture tasks
wait "$cubic_pid"
wait "$bbr_pid"
wait "$capture_cubic_pid"
wait "$capture_bbr_pid"

echo "Done. Files saved:"
echo "CUBIC -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
echo "BBR   -> $BBR_JSON, $BBR_STDOUT, $BBR_SS_TXT"

