
# #!/bin/sh

# SERVER_IP="192.168.4.38"
# DURATION=20
# INTERVAL=1
# PORT_CUBIC=5201
# PORT_BBR=5202

# # Create output directories
# mkdir -p cubic_flow
# mkdir -p bbr3_flow

# # File paths
# CUBIC_JSON="cubic_flow/cubic_vs_bbr3_cubic.json"
# CUBIC_STDOUT="cubic_flow/cubic_vs_bbr3_cubic_stdout.txt"
# CUBIC_SS_TXT="cubic_flow/cubic_vs_bbr3_cubic_ss.txt"

# BBR_JSON="bbr3_flow/cubic_vs_bbr3_bbr.json"
# BBR_STDOUT="bbr3_flow/cubic_vs_bbr3_bbr_stdout.txt"
# BBR_SS_TXT="bbr3_flow/cubic_vs_bbr3_bbr_ss.txt"

# # Function to capture ss -ti output
# capture_ss() {
#   fname=$1
#   port_filter=$2
#   i=0
#   while [ $i -lt $DURATION ]; do
#     echo "=== $(date '+%T') ===" >> "$fname"
#     ss -ti | grep "$port_filter" -A 1 >> "$fname"
#     echo "" >> "$fname"
#     i=$((i + 1))
#     sleep 1
#   done
# }

# echo "=== Starting both flows and captures simultaneously ==="

# # Start both iperf3 flows
# timeout $((DURATION + 5)) iperf3 -c "$SERVER_IP" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
# cubic_pid=$!

# timeout $((DURATION + 5)) iperf3 -c "$SERVER_IP" -p "$PORT_BBR" -C bbr -t "$DURATION" -i "$INTERVAL" -J > "$BBR_JSON" 2> "$BBR_STDOUT" &
# bbr_pid=$!

# # Start ss capture in background
# capture_ss "$CUBIC_SS_TXT" ":$PORT_CUBIC" &
# capture_cubic_pid=$!

# capture_ss "$BBR_SS_TXT" ":$PORT_BBR" &
# capture_bbr_pid=$!

# # Wait for all background jobs
# wait "$cubic_pid"
# wait "$bbr_pid"
# wait "$capture_cubic_pid"
# wait "$capture_bbr_pid"

# echo "=== All tests complete ==="
# echo "Cubic flow files -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
# echo "BBR3 flow files  -> $BBR_JSON, $BBR_STDOUT, $BBR_SS_TXT"


#!/bin/sh

# Receiver IPs for each flow
SERVER_IP_CUBIC="192.168.10.50"  # Receiver laptop for Cubic
SERVER_IP_BBR="192.168.10.45"    # Receiver laptop for BBR

DURATION=20
INTERVAL=1
PORT_CUBIC=5201
PORT_BBR=5202

# Create output directories
mkdir -p cubic_flow
mkdir -p bbr3_flow

# File paths
CUBIC_JSON="cubic_flow/cubic_vs_bbr3_cubic.json"
CUBIC_STDOUT="cubic_flow/cubic_vs_bbr3_cubic_stdout.txt"
CUBIC_SS_TXT="cubic_flow/cubic_vs_bbr3_cubic_ss.txt"

BBR_JSON="bbr3_flow/cubic_vs_bbr3_bbr.json"
BBR_STDOUT="bbr3_flow/cubic_vs_bbr3_bbr_stdout.txt"
BBR_SS_TXT="bbr3_flow/cubic_vs_bbr3_bbr_ss.txt"

# Function to capture ss -ti output filtered by port
capture_ss() {
  fname=$1
  port_filter=$2
  i=0
  while [ $i -lt $DURATION ]; do
    echo "=== $(date '+%T') ===" >> "$fname"
    ss -ti | grep "$port_filter" -A 1 >> "$fname"
    echo "" >> "$fname"
    i=$((i + 1))
    sleep 1
  done
}

echo "=== Starting both flows and captures simultaneously ==="

# Start iperf3 flow for Cubic to SERVER_IP_CUBIC
timeout $((DURATION + 5)) iperf3 -c "$SERVER_IP_CUBIC" -p "$PORT_CUBIC" -C cubic -t "$DURATION" -i "$INTERVAL" -J > "$CUBIC_JSON" 2> "$CUBIC_STDOUT" &
cubic_pid=$!

# Start iperf3 flow for BBR to SERVER_IP_BBR
timeout $((DURATION + 5)) iperf3 -c "$SERVER_IP_BBR" -p "$PORT_BBR" -C bbr -t "$DURATION" -i "$INTERVAL" -J > "$BBR_JSON" 2> "$BBR_STDOUT" &
bbr_pid=$!

# Start ss capture in background for Cubic port on local machine
capture_ss "$CUBIC_SS_TXT" ":$PORT_CUBIC" &
capture_cubic_pid=$!

# Start ss capture in background for BBR port on local machine
capture_ss "$BBR_SS_TXT" ":$PORT_BBR" &
capture_bbr_pid=$!

# Wait for all background jobs to finish
wait "$cubic_pid"
wait "$bbr_pid"
wait "$capture_cubic_pid"
wait "$capture_bbr_pid"

echo "=== All tests complete ==="
echo "Cubic flow files -> $CUBIC_JSON, $CUBIC_STDOUT, $CUBIC_SS_TXT"
echo "BBR3 flow files  -> $BBR_JSON, $BBR_STDOUT, $BBR_SS_TXT"
