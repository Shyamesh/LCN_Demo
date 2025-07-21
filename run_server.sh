#!/bin/bash

# Must run the whole script as sudo!
if [[ $EUID -ne 0 ]]; then
   echo "Please run as root (use: sudo ./run_server.sh)"
   exit 1
fi

# Start iperf3 servers in background
iperf3 -s -p 5201 > iperf_5201.log 2>&1 &
PID1=$!
iperf3 -s -p 5202 > iperf_5202.log 2>&1 &
PID2=$!

# Start a single tcpdump for both ports
tcpdump -i any 'port 5201 or port 5202' -w combined_capture.pcapng &
TCPDUMP=$!

# Ensure cleanup on exit
trap "kill $TCPDUMP $PID1 $PID2 2>/dev/null; echo 'Processes terminated'; exit" EXIT

echo "Servers and capture running. Press any key to stop..."
read -n 1

echo "Capture complete. File saved: combined_capture.pcapng"

