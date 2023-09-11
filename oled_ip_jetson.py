#https://github.com/NVIDIA-AI-IOT/jetbot/blob/master/jetbot/apps/stats.py
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import os.path

import Jetson.GPIO as GPIO

board_name=GPIO.gpio_pin_data.get_data()[0]
print(board_name)
if board_name == "JETSON_NX":
    i2c_busnum = 8
elif board_name == "JETSON_XAVIER":
    i2c_busnum = 8
elif board_name == "JETSON_NANO":
    i2c_busnum = 1
elif board_name == "JETSON_ORIN":
    i2c_busnum = 7
elif board_name == "JETSON_ORIN_NX":
    i2c_busnum = 7
elif board_name == "JETSON_ORIN_NANO":
    i2c_busnum = 7

def get_ip_address(interface):
    interface_state = get_network_interface_state(interface)
    if interface_state is None: # No interface found
        return None
    elif interface_state == 'down':
        return None

    cmd = "ifconfig %s | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'" % interface
    return subprocess.check_output(cmd, shell=True).decode('ascii')[:-1]


def get_network_interface_state(interface):
    if os.path.isfile('/sys/class/net/%s/operstate' % interface):
        return subprocess.check_output('cat /sys/class/net/%s/operstate' % interface, shell=True).decode('ascii')[:-1]
    else:
        # No interface found
        return None

def main():
    # 128x32 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=i2c_busnum, gpio=1) # setting gpio to 1 is hack to avoid platform detection
    

    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    # Load default font.
    font = ImageFont.load_default()

    count = 0
    while True:

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True )

        # Write two lines of text.
        eth0 = str(get_ip_address('eth0'))
        wlan0 = str(get_ip_address('wlan0'))
        draw.text((x, top),       "eth0:" + eth0,   font=font, fill=255)
        draw.text((x, top+8),     "wlan0:" + wlan0, font=font, fill=255)
        draw.text((x, top+16),    str(MemUsage.decode('utf-8')),  font=font, fill=255)
        draw.text((x, top+25),    str(Disk.decode('utf-8')),  font=font, fill=255)

        # Display image.
        disp.image(image)
        disp.display()
        if (eth0 == 'None' or wlan0 == 'None') and count < 10:
            # network searching
            time.sleep(1)
            count += 1
        elif (eth0 != 'None' or wlan0 != 'None'):
            # network is available
            time.sleep(1)
        else:
            # no network
            break

if __name__ == "__main__":
    ########################################
    # OLED I2C address check
    ########################################
    import smbus
    bus = smbus.SMBus(i2c_busnum) # 1 indicates /dev/i2c-1
    i2c_address = 0x3C
    try:
        bus.read_byte(i2c_address)
        main()
    except:
        # no oled
        pass
