#!/bin/bash

/home/$(getent passwd 1000 | cut -d: -f1)/env/bin/python /home/$(getent passwd 1000 | cut -d: -f1)/fabo/bin/oled_ip.py 
