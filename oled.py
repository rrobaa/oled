import Adafruit_SSD1306
import psutil
from PIL import Image, ImageDraw, ImageFont
import time
import threading
import subprocess


# Initialize the SSD1306 display
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
disp.begin()
disp.clear()
disp.display()

# Create a blank image for drawing
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on the image
draw = ImageDraw.Draw(image)

# Set different font sizes for each text line
font_ip = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
font_others = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

# Variables to hold system stats
cpu_usage = 0
memory_usage = 0
hdd_usage = 0

# Function to get IP address
def get_ip_address():
    addrs = psutil.net_if_addrs()
    if 'eth0' in addrs:
        return addrs['eth0'][0].address
    elif 'wlan0' in addrs:
        return addrs['wlan0'][0].address
    else:
        return "No IP found"

# Function to read CPU temperature
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as file:
            temperature = file.read()
        temperature = round(float(temperature) / 1000.0, 1)
        return temperature
    except FileNotFoundError:
        return None

# Function to update system stats in the background
def update_stats():
    global cpu_usage, memory_usage, hdd_usage
    while True:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        hdd_usage = psutil.disk_usage('/').percent
        time.sleep(2)  # Adjust the sleep duration to control how often stats are updated

# Start the background thread to update system stats
stats_thread = threading.Thread(target=update_stats)
stats_thread.daemon = True
stats_thread.start()


# Global variables for networkcheck
wan = ""
router = ""
switch = ""
ap01 = ""
ap02 = ""

device_statuses = {}

def check_device_status(device_ip):
    # Use the 'ping' command with subprocess
    process = subprocess.Popen(['ping', '-c', '1', device_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = process.communicate()

    if process.returncode == 0:
        return device_ip
    else:
        return "DOWN"

devices = {
    "wan": "8.8.8.8",
    "router": "192.168.1.1",
    "switch": "192.168.1.2",
    "ap01": "192.168.1.3",
    "ap02": "192.168.1.4"
}


# Ping network
def network_check():
    for device, ip in devices.items():
        status = check_device_status(ip)
        device_statuses[device] = status
    
    wan = device_statuses.get("wan", "DOWN")
    router = device_statuses.get("router", "DOWN")
    switch = device_statuses.get("switch", "DOWN")
    ap01 = device_statuses.get("ap01", "DOWN")
    ap02 = device_statuses.get("ap02", "DOWN")
    time.sleep(10)

# Start the background thread of pining network
network_thread = threading.Thread(target=network_check)
network_thread.daemon = True
network_thread.start()


# Function to update display with live system stats
def update_display():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), f"IP: {get_ip_address()}", font=font_ip, fill=255)
    draw.text((0, 18), f"CPU:".ljust(7) + f"{cpu_usage}%", font=font_others, fill=255)
    draw.text((0, 30), f"Temp:".ljust(7) + f"{get_cpu_temperature()} °C", font=font_others, fill=255)
    draw.text((0, 42), f"MEM:".ljust(7) + f"{memory_usage}%", font=font_others, fill=255)
    draw.text((0, 54), f"HDD:".ljust(7) + f"{hdd_usage}%", font=font_others, fill=255)

    disp.image(image)
    disp.display()

def check_network():
    network_check()
    return True

def show_network_status():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), f"WAN: {wan}", font=font_others, fill=255)
    draw.text((0, 12), f"Router: {router}", font=font_others, fill=255)



    disp.image(image)
    disp.display()



# Continuously update the display every 2 seconds
update_timer = 0
while True:
#    if update_timer == 5: # Change to whats needed
#        update = check_network()
#        if update:
#            show_network_status()
#            time.sleep(10)
#            update_timer = 0
    update_display()
    time.sleep(2)
    update_timer += 1
    print(update_timer)
