#!/usr/bin/python

##get_ip example##
import os
import time
from sense_hat import SenseHat
import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

sense = SenseHat()
sense.set_rotation(90)
deco = (155, 0, 155)
sense.show_message(get_ip(), text_colour=deco)