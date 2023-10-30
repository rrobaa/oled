import Adafruit_SSD1306
import psutil
from PIL import Image, ImageDraw, ImageFont
from time import sleep
# import time
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

        sleep(2)  # Adjust the sleep duration to control how often stats are updated

# Start the background thread to update system stats
stats_thread = threading.Thread(target=update_stats)
stats_thread.daemon = True
stats_thread.start()

# Function to update display with live system stats
def update_display():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), f"IP: {get_ip_address()}", font=font_ip, fill=255)
    draw.text((0, 18), f"CPU:".ljust(7) + f"{cpu_usage}%", font=font_others, fill=255)
    draw.text((0, 30), f"Temp:".ljust(7) + f"{get_cpu_temperature()} °C", font=font_others, fill=255)
    draw.text((0, 42), f"MEM:".ljust(7) + f"{memory_usage}%", font=font_others, fill=255)
    draw.text((0, 54), f"HDD: ".ljust(5), font=font_others, fill=255)

    # Draw a bar graph for HDD space
    hdd_bar_width = 50
    hdd_bar_height = 7
    hdd_bar_x = 40
    hdd_bar_y = 56 # Added 2 so it looked better on screen

    # Calculate the width of the used portion of the bar
    used_space = int((hdd_bar_width * hdd_usage) / 100)
    draw.rectangle((hdd_bar_x, hdd_bar_y, hdd_bar_x + hdd_bar_width, hdd_bar_y + hdd_bar_height), outline=1, fill=0)
    draw.rectangle((hdd_bar_x, hdd_bar_y, hdd_bar_x + used_space, hdd_bar_y + hdd_bar_height), outline=1, fill=1)

    # Display the HDD usage percentage just behind the bar
    draw.text((hdd_bar_x + hdd_bar_width + 2, hdd_bar_y - 2), f"{hdd_usage}%", font=font_others, fill=1)

    disp.image(image)
    disp.display()

# Start of ping sequens
device_statuses = {
    "WAN": "UNKNOWN",
    "Router": "UNKNOWN",
    "Switch": "UNKNOWN",
    "AP01": "UNKNOWN",
    "AP02": "UNKNOWN"
}

def ping_device(device):
    result = subprocess.call(['ping', '-c', '1', device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "UP" if result == 0 else "DOWN"

def check_device_status():
    while True:
        # Ping WAN (Google's DNS)
        wan_status = ping_device('8.8.8.8')
        device_statuses["WAN"] = wan_status

        # Ping Router
        router_ip = '192.168.1.1'
        router_status = ping_device(router_ip)
        device_statuses["Router"] = router_ip if router_status == 'UP' else 'DOWN'

        # Ping Switch
        switch_ip = '192.168.1.2'
        switch_status = ping_device(switch_ip)
        device_statuses["Switch"] = switch_ip if switch_status == 'UP' else 'DOWN'

        # Ping Access Point 01
        ap01_ip = '192.168.1.11'
        ap01_status = ping_device(ap01_ip)
        device_statuses["AP01"] = ap01_ip if ap01_status == 'UP' else 'DOWN'

        # Ping Access Point 02
        ap02_ip = '192.168.1.12'
        ap02_status = ping_device(ap02_ip)
        device_statuses["AP02"] = ap02_ip if ap02_status == 'UP' else 'DOWN'

        sleep(10)  # Wait for 10 seconds before pinging again

# Create a thread for the device status checking
device_thread = threading.Thread(target=check_device_status)
device_thread.daemon = True  # Set the thread as daemon to exit when the main program exits
device_thread.start()

def network_display():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), f"WAN: Internet {device_statuses['WAN']}", font=font_others, fill=255)
    draw.text((0, 12), f"FR01: {device_statuses['Router']}", font=font_others, fill=255)
    draw.text((0, 24), f"SW01: {device_statuses['Switch']}", font=font_others, fill=255)
    draw.text((0, 36), f"AP01: {device_statuses['AP01']}", font=font_others, fill=255)
    draw.text((0, 48), f"AP02: {device_statuses['AP02']}", font=font_others, fill=255)

    disp.image(image)
    disp.display()



# TEST FOR SPINNING RPI LOGO ON STARTUP
# def display_static_logo(duration=5):
#     logo = Image.open('rpi-logo.png').convert('1')  # Replace with your logo file path

#     # Assuming you have these variables defined somewhere
#     width = 128  # Replace with the appropriate display width
#     height = 64  # Replace with the appropriate display height
#     image = Image.new('1', (width, height))
#     draw = ImageDraw.Draw(image)

#     # Calculate the position for the logo
#     x = (width - logo.width) // 2
#     y = (height - logo.height) // 2

#     disp.image(image)
#     disp.display()

#     # Show the static logo for 5 seconds
#     start_time = time.time()
#     while (time.time() - start_time) < duration:
#         draw.rectangle((0, 0, width, height), outline=0, fill=0)
#         draw.bitmap((x, y), logo, fill=1)
#         disp.image(image)
#         disp.display()
#         time.sleep(0.1)  # Adjust sleep time if needed

# Continuously update the display every 2 seconds
update_timer = 0

# display_static_logo()

while True:
    if update_timer == 5: # Change to whats needed
        network_display()
        sleep(10)
        update_timer = 0
    update_display()
    sleep(2)
    update_timer += 1
