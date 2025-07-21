#!/bin/bash
#  
# Must run the whole script as sudo!
if [[ $EUID -ne 0 ]]; then
   echo "Please run as root (use: sudo ./run_server2.sh)"
   exit 1
fi

cd 
cd /home/sit/Desktop/tcp_data/

# Ensure directories exist
OUTPUT_DIR="/home/sit/Desktop/tcp_data/bbr3_vs_cubic_output"
mkdir -p "$OUTPUT_DIR"

# Start iperf3 server in background (only one flow on port 5201)
echo "Starting iperf3 server..."
iperf3 -s -p 5201 > "$OUTPUT_DIR/iperf_5201.log" 2>&1 &
PID1=$!

# Start tcpdump for port 5201 only
echo "Starting tcpdump..."
tcpdump -i any 'port 5201' -w "$OUTPUT_DIR/combined_capture.pcapng" &
TCPDUMP=$!

# Ensure cleanup on exit
trap "kill $TCPDUMP $PID1 2>/dev/null; echo 'Processes terminated'; exit" EXIT

# Track first JSON entry separately
first_entry=true

# Periodically capture ss -tin output and save metrics in a JSON array format
echo "[" > "$OUTPUT_DIR/tcp_metrics.json"  # Open JSON array

while true; do
    timestamp=$(date --iso-8601=seconds)
    echo "Capturing metrics at $timestamp"

    ss -tin > "$OUTPUT_DIR/ss_output.txt"

    # Convert Bash boolean to Python boolean
    py_bool="True"
    if [ "$first_entry" != "true" ]; then
        py_bool="False"
    fi

    python3 << EOF
import json, re, os

output_dir = os.path.expanduser("$OUTPUT_DIR")
ss_path = os.path.join(output_dir, 'ss_output.txt')
json_path = os.path.join(output_dir, 'tcp_metrics.json')

metrics = []
entry = {}
timestamp = "$timestamp"
first_entry = $py_bool

with open(ss_path) as f:
    for line in f:
        line = line.strip()

        # Start of a new socket entry
        if re.match(r'^(ESTAB|LISTEN|CLOSE-WAIT|SYN-RECV|TIME-WAIT|FIN-WAIT|CLOSE|LAST-ACK|UNKNOWN)', line):
            if entry:
                metrics.append(entry)
                entry = {}
            entry['timestamp'] = timestamp
            entry['state_line'] = line
        else:
            parts = re.findall(r'(\w+:\S+)', line)
            for part in parts:
                try:
                    k, v = part.split(':', 1)
                    entry[k.strip()] = v.strip()
                except ValueError:
                    continue

    if entry:
        metrics.append(entry)

with open(json_path, 'a') as out:
    if not first_entry:
        out.write(",\n")
    json.dump(metrics, out, indent=2)

EOF

    first_entry=false
    sleep 1
done

