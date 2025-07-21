# #!/bin/bash

# SERVER_IP="192.168.10.55"
# DURATION=120  # Duration in seconds
# INTERVAL=1

# PORT_CUBIC=5201
# PORT_BBR2=5202

# # Output files
# CUBIC_JSON="cubic_results.json"
# CUBIC_STDOUT="cubic_stdout.txt"
# CUBIC_SS_TXT="cubic_ss.txt"

# BBR2_JSON="bbr2_results.json"
# BBR2_STDOUT="bbr2_stdout.txt"
# BBR2_SS_TXT="bbr2_ss.txt"

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
# iperf3 -c "$SERVER_IP" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J  > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
# cubic_pid=$!

# # Start BBR2 flow
# echo "Starting BBR2 flow..."
# capture_ss "$BBR2_SS_TXT" &
# capture_bbr2_pid=$!
# iperf3 -c "$SERVER_IP" -p "$PORT_BBR2" -C bbr2 -t "$DURATION" -i "$INTERVAL" -J > "$BBR2_JSON" 2> "$BBR2_STDOUT" &
# bbr2_pid=$!

# # Wait for both flows to finish
# wait "$cubic_pid"
# wait "$bbr2_pid"
# wait "$capture_cubic_pid"
# wait "$capture_bbr2_pid"

# echo "Done. Files saved:"
# echo "CUBIC -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
# echo "BBR2  -> $BBR2_JSON, $BBR2_STDOUT, $BBR2_SS_TXT"



#!/bin/bash

SERVER_IP_CUBIC="192.168.10.50"
SERVER_IP_BBR2="192.168.10.55"

DURATION=120  # Duration in seconds
INTERVAL=1

PORT_CUBIC=5201
PORT_BBR2=5202

# Output files
CUBIC_JSON="cubic_results.json"
CUBIC_STDOUT="cubic_stdout.txt"
CUBIC_SS_TXT="cubic_ss.txt"

BBR2_JSON="bbr2_results.json"
BBR2_STDOUT="bbr2_stdout.txt"
BBR2_SS_TXT="bbr2_ss.txt"

# Function to capture TCP socket stats filtered by port
function capture_ss() {
  local fname=$1
  local port=$2
  for ((i=0; i<$DURATION; i++)); do
    echo "=== $(date '+%T') ===" >> "$fname"
    ss -tin | grep ":$port" -A 10 >> "$fname"
    echo -e "\n" >> "$fname"
    sleep 1
  done
}

# Start CUBIC flow
echo "Starting CUBIC flow..."
capture_ss "$CUBIC_SS_TXT" "$PORT_CUBIC" &
capture_cubic_pid=$!
iperf3 -c "$SERVER_IP_CUBIC" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
cubic_pid=$!

# Start BBR2 flow
echo "Starting BBR2 flow..."
capture_ss "$BBR2_SS_TXT" "$PORT_BBR2" &
capture_bbr2_pid=$!
iperf3 -c "$SERVER_IP_BBR2" -p "$PORT_BBR2" -C bbr2 -t "$DURATION" -i "$INTERVAL" -J > "$BBR2_JSON" 2> "$BBR2_STDOUT" &
bbr2_pid=$!

# Wait for both flows and captures to finish
wait "$cubic_pid"
wait "$bbr2_pid"
wait "$capture_cubic_pid"
wait "$capture_bbr2_pid"

echo "Done. Files saved:"
echo "CUBIC -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
echo "BBR2  -> $BBR2_JSON, $BBR2_STDOUT, $BBR2_SS_TXT"
