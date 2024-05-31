# Importing Libraries 
import serial 
import time 
import keyboard
from datetime import datetime, timedelta

# arduino = serial.Serial(port='/dev/cu.usbmodem111659401', baudrate=9600, timeout=.1)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

# start sensor ouput from arduino
# def write(data_type):
# 	arduino.write(b"\nSETREPRATE  500\n") 
# 	time.sleep(5)

# 	if data_type == 'raw':
# 		arduino.write(b"\nRSEN  1\n") 
# 	if data_type == 'induction':
# 		arduino.write(b"\nRSEN  0\n")
# 	if data_type == 'both':
# 		arduino.write(b"\nRSEN  2\n")
# 	time.sleep(0.05)

	

# write measurement data to csv
def to_csv(timestamp, measurement_id, sensor_id, weight, sensor_data):
	with open(f"sensor_{sensor_id}.csv", "a") as file:
				id_sensor_data= str(measurement_id) + "," + str(sensor_id) + "," + weight + "," + str(timestamp) + "," + sensor_data + "\n"
				file.write(id_sensor_data)
				

# Measurement variables
# One csv file for each sensor
print("Starting...") 
# write('raw')
measurement_id = 0

weight = "700"
arduino.readline().decode().strip()

time.sleep(0.05)

# print("start", start)
while True: 
	data = arduino.readline().decode().strip()
	if keyboard.is_pressed('r'):
		print("resetting")
		measurement_id = 0
	if keyboard.is_pressed('i'):
		sensor_id = input("sensor id:")
	print(data)

	
	if keyboard.is_pressed('m'):
		print(measurement_id-1)

	if keyboard.is_pressed('w'):
		
		print("Saving...", measurement_id)

		n = 0
		while n < 40:
			data = arduino.readline().decode().strip() 
			timestamp = datetime.now()
	
			if data != "" and data[0] != 'S' and data[0] != 'D':
				print(data)
				to_csv(timestamp, measurement_id, sensor_id, weight, data)
				n += 1
		print("Saved...")
		measurement_id += 1
		
	elif keyboard.is_pressed("q"):
		print("Escape hit, closing...")
		break