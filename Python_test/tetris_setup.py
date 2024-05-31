# Importing Libraries 
import serial 
import time 
import keyboard
from datetime import datetime, timedelta
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from keras.models import load_model
import math
import random


img_counter = 0
cam = cv2.VideoCapture(0)
# arduino = serial.Serial(port='/dev/cu.usbmodem111659401', baudrate=9600, timeout=.1)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
	
# write measurement data to csv
def to_csv(timestamp, experiment_id, measurement_id, tetris_id, weight, sensor_data):
	with open(f"tetris_{tetris_id}_4.csv", "a") as file:
				id_sensor_data= str(experiment_id) + "," + str(measurement_id) + "," + str(tetris_id) + "," + weight + "," + str(timestamp) + "," + sensor_data + "\n"
				file.write(id_sensor_data)
				

# Measurement variables
# One csv file for each sensor
print("Starting...") 
# write('raw')
measurement_id = 0
base_id = 0

weight = "229"
experiment_id = 0
arduino.readline().decode().strip()

time.sleep(0.05)
model = load_model("tuned_model1234.h5")

# direction = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
# step = ['0', '2', '4']
# tetris_list = ['I', 'T', 'Z', 'O', 'L']


def convert_inductance(df):
    id_list = ['B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4']
    for id in id_list:
        df[id] = df[id].apply(lambda raw: ((1000000 * ( ( 2**25 ) / (math.pi * raw))**2)))
    return df

# print("start", start)
while True: 
	data = arduino.readline().decode().strip()
	if keyboard.is_pressed('r'):
		print("resetting")
		measurement_id = 0

	if keyboard.is_pressed('i'):
		tetris_id = input("tetris id:")
	# print(data)

	# if keyboard.is_pressed('d'):
		# direction = input("Direction:")
		# step = 0

	# BASELINE
	if keyboard.is_pressed('b'):
		
		print("Saving baseline..")
		n = 0
		#direction_step = direction + str(step)
		# direction_step = random.choice(direction) + random.choice(step)
		# tetris_id = random.choice(tetris_list)
		baseline = pd.DataFrame(columns = ['Experiment_id', 'Measurement_id', 'Tetris_id',  'Timestamp', 'B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4'])
		
		while n < 40:
			data = arduino.readline().decode().strip() 
			print(data)
			timestamp = datetime.now()

			# if n % 10 == 0: 
			# 	print(data)

			if data != "" and data[0] != 'S' and data[0] != 'D':
				with open(f"tetris{tetris_id}_baseline_4.csv", "a") as file:
					id_sensor_data = str(experiment_id) + "," + str(measurement_id) + "," + str(tetris_id) + "," + str(timestamp) + "," + data + "\n"
					file.write(id_sensor_data)
				
				#data = data.split(',')
				#sensor_data = [float(sens) for sens in data[:-1]]

				new_row = [experiment_id, measurement_id, tetris_id , str(timestamp)] + [float(sens) for sens in data.split(',')[:-1]]
				print(new_row)
				baseline.loc[len(baseline)] = new_row
			n += 1
		
		df_base_grouped = baseline.groupby(['Experiment_id', 'Measurement_id', 'Tetris_id']).agg({id: ['mean'] for id in ['B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4']})
		df_base_grouped = df_base_grouped.droplevel(1, axis=1)
		print(df_base_grouped)
		base_id += 1
		print("Saved...")
		# print(tetris_id, direction_step)

	if keyboard.is_pressed('m'):
		print(measurement_id-1)

	# MEASUREMENT
	if keyboard.is_pressed('w'):
		if base_id == measurement_id:
			print("Baseline Missing!")

		else:
			tetris = pd.DataFrame(columns = ['Experiment_id', 'Measurement_id', 'Tetris_id',  'Timestamp', 'B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4'])
			print("Saving...", measurement_id)

			ret, frame = cam.read()
			if not ret:
				print("failed to grab frame")
				break


			k = cv2.waitKey(1)

			img_name = f"opencv_tetris_{experiment_id}_{tetris_id}_{measurement_id}.png".format(experiment_id, tetris_id, measurement_id)
			cv2.imwrite(img_name, frame)
			print("{} written!".format(img_name))
			#direction_step = direction + str(step)
			n = 0
			while n < 40:
				data = arduino.readline().decode().strip() 
				timestamp = datetime.now()

				# if n % 10 == 0: 
				# 	print(data)

				if data != "" and data[0] != 'S' and data[0] != 'D':
					to_csv(timestamp, experiment_id, measurement_id, tetris_id,  weight, data)
					n += 1

		
					new_row = [experiment_id, measurement_id, tetris_id, timestamp] + [float(sens) for sens in data.split(',')[:-1]]
					tetris.loc[len(tetris)] = new_row

			df_tetris_grouped = tetris.groupby(['Experiment_id', 'Measurement_id', 'Tetris_id']).agg({id: ['mean'] for id in ['B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4']})
			df_tetris_grouped = df_tetris_grouped.droplevel(1, axis=1)

			df_tetris_grouped_indu = convert_inductance(df_tetris_grouped)
			df_base_grouped_indu = convert_inductance(df_base_grouped)

			baselined_measurement = df_tetris_grouped_indu.sub(df_base_grouped_indu)
			
			# Run through model
			X = baselined_measurement[['B2', 'B1', 'A2', 'A1', 'B3', 'B0', 'A3', 'A0', 'B6', 'B5', 'A6', 'A5', 'B7', 'B4', 'A7', 'A4']]
			y = tetris_id
			labels = np.array(['I', 'L', 'O', 'T', 'Z'])
			
			y_one_hot = np.zeros(len(labels))
			index = np.where(labels == y)
			y_one_hot[index] = 1
			print(tetris_id, y_one_hot)

			prediction = model.predict(X)
			print(prediction)
			
			predicted = labels[np.argmax(prediction[0])]
			actual = labels[np.argmax(y_one_hot)]
			print('Predicted label:', predicted, '\nActual label:', actual)
	
			
			print("Saved...")
			measurement_id += 1
			#step += 1
			time.sleep(1)
		
	elif keyboard.is_pressed("q"):
		print("Escape hit, closing...")
		break