import serial 
import time 
import keyboard
from datetime import datetime, timedelta




arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

arduino.write(b"\nSRSEN0\n") 
time.sleep(0.05)

