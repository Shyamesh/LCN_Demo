####################################
# 1. Reset and Basic Configuration
####################################

/system reset-configuration no-defaults=yes

# Disable all unused Ethernet ports
/interface ethernet
set ether1 disabled=yes
set ether2 disabled=yes
set ether3 disabled=yes
set ether4 disabled=yes
set ether5 disabled=yes

# Create a bridge for WiFi
/interface bridge
add name=bridge1

/interface bridge port
add bridge=bridge1 interface=wifi2

# Assign static IP for router (gateway)
/ip address
add address=192.168.88.1/24 interface=bridge1

####################################
# 2. WiFi Configuration (2.4GHz Only)
####################################

/interface wifiwave2 set [find name=wifi2] \
  channel.band=2ghz-ax \
  channel.width=20mhz \
  configuration.ssid="Mikrotik2" \
  security.authentication-types=wpa2-psk \
  security.passphrase="12345" \
  mode=ap

# Disable 5GHz interface if not used
/interface wifiwave2 set [find name=wifi1] disabled=yes

####################################
# 3. Queuing and Traffic Shaping
####################################

# Set global queue type and limits
/queue type set default-small kind=pfifo limit=20

# Create a simple queue limiting total bandwidth
/queue simple
add name=Total_Limit target=bridge1 max-limit=10M/10M

# Optional: experiment with more fine-grained limits (if needed)/queprint
# /queue simple add name=Client_Limit target=192.168.88.100/32 max-limit=10M/10M

####################################
# 4. TCP Performance Optimization
####################################

# Disable hardware offload (important for queueing/monitoring)
/interface wifiwave2 set [find name=wifi2] hw-offload=no

# Optimize TCP stack for lab testing
/ip settings
set tcp-syncookies=no
set tcp-max-syn-backlog=2048

####################################
# 5. Firewall Rules (for full isolation)
####################################

/ip firewall connection tracking set enabled=yes

/ip firewall filter
add chain=forward action=accept in-interface=bridge1 out-interface=bridge1
add chain=forward action=drop out-interface=ether2


####################################
# 6. Monitoring Tools
####################################

# Print router, CPU, and interface status
/system resource print
/system resource cpu print
/interface print
/ip address print

# Real-time bandwidth per interface
/interface monitor-traffic bridge1 once

# Torch (live packet inspection)
/tool torch interface=bridge1 port=any protocol=tcp

# Queue stats
/queue simple print stats

# Capture packets for offline analysis
/tool packet-sniffer start interface=bridge1 file-name=tcp_research.pcap memory-scroll=no

/interface wifiwave2 set wifi2 \ security.passphrase=12345678
