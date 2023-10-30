import subprocess

# List of devices to ping
devices = ['192.168.1.1', '192.168.1.2', '192.168.1.3']

def ping_device(device):
    # Use the ping command with count 1 (one packet)
    with open('/dev/null', 'w') as DEVNULL:
        result = subprocess.call(['ping', '-c', '1', device], stdout=DEVNULL, stderr=DEVNULL)
    
    if result == 0:
        print(f"{device} is reachable")
    else:
        print(f"{device} is unreachable")

# Ping each device in the list
for device in devices:
    ping_device(device)
