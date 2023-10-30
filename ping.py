import subprocess
import time

def ping_device(device):
    result = subprocess.call(['ping', '-c', '1', device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "UP" if result == 0 else "DOWN"

while True:
    # Ping WAN (Google's DNS)
    wan_status = ping_device('8.8.8.8')
    print(f"WAN: {wan_status}")

    # Ping Router
    router_ip = '192.168.1.1'
    router_status = ping_device(router_ip)
    print(f"Router: {router_ip if router_status == 'UP' else 'DOWN'}")

    # Ping Switch
    switch_ip = '192.168.1.2'
    switch_status = ping_device(switch_ip)
    print(f"Switch: {switch_ip if switch_status == 'UP' else 'DOWN'}")

    # Ping Access Point 01
    ap01_ip = '192.168.1.3'
    ap01_status = ping_device(ap01_ip)
    print(f"AP01: {ap01_ip if ap01_status == 'UP' else 'DOWN'}")

    # Ping Access Point 02
    ap02_ip = '192.168.1.4'
    ap02_status = ping_device(ap02_ip)
    print(f"AP02: {ap02_ip if ap02_status == 'UP' else 'DOWN'}")

    time.sleep(10)  # Wait for 10 seconds before pinging again
