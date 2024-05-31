import serial 
import time 
import keyboard
from datetime import datetime, timedelta




arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

arduino.write(b"\nSETREPRATE  50\n") 
time.sleep(0.05)
arduino.write(b"\nRSEN  1\n") 
time.sleep(0.05)
