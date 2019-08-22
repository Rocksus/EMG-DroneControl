# Drone Control
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import keyboard
# Myo
import myo
# Keras Neural Network
from keras.models import load_model
from collections import deque
import numpy as np

sampleLength = 32


def arm_and_takeoff(vehicle,aTargetAltitude):
	"""
	Arms vehicle and fly to aTargetAltitude.
	"""

	print ("Basic pre-arm checks")

	# Don't try to arm until autopilot is ready
	# Except when you are feeling reckless****
	# And being reckless is fun.

	# while not vehicle.is_armable:
	# 	print (" Waiting for vehicle to initialise...")
	# 	time.sleep(1)

	print ("Arming motors")
	# Copter should arm in GUIDED mode
	vehicle.mode    = VehicleMode("GUIDED")
	vehicle.armed   = True

	# Confirm vehicle armed before attempting to take off
	while not vehicle.armed:
		print (" Waiting for arming...")
		vehicle.armed = True
		time.sleep(1)

	print ("Taking off!")
	vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

	# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
	#  after Vehicle.simple_takeoff will execute immediately).
	while True:
		print (" Altitude: %.1f m"%vehicle.location.global_relative_frame.alt)
		#Break and return from function just below target altitude.
		if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
			print ("Reached target altitude")
			break
		time.sleep(1)

def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z):
	"""
	Move vehicle in direction based on specified velocity vectors.
	"""
	msg = vehicle.message_factory.set_position_target_local_ned_encode(
		0,       # time_boot_ms (not used)
		0, 0,    # target system, target component
		mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
		0b0000111111000111, # type_mask (only speeds enabled)
		0, 0, 0, # x, y, z positions (not used)
		velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
		0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
		0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)


	vehicle.send_mavlink(msg)
	vehicle.flush()

#Listener Class
class Listener(myo.DeviceListener):
	# it will only listen to emg data and
	# make a 20 step queue from it.
	def __init__(self):
		self.emg_data = deque(maxlen=sampleLength)

	def get_emg_data(self):
		return list(self.emg_data)

	def on_connected(self, event):
		print('Myo Connected!')
		event.device.stream_emg(True)

	def on_emg(self, event):
		self.emg_data.append(event.emg)

if __name__ == '__main__':
	connection_string = 'udp:127.0.0.1:14551'
	gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

	# Setup the command flying speed
	gnd_speed = 5 # m/s
	myo.init(sdk_path='../myo-sdk-win-0.9.0')
	hub = myo.Hub()
	listener = Listener()

	print('Loading Model...')
	# Load Model
	model = load_model('../EMG_Model_CNN_RNN.h5')

	# View summary of model
	model.summary()

	vehicle_flying = False

	print('Connecting..')
	# Try Connecting to drone
	vehicle = connect(connection_string, wait_ready=True)
	vehicle.flush()
	print('Ready to send commands!')
	while hub.run(listener.on_event, 500):
		emg = np.array(listener.get_emg_data())
		while(len(emg)<sampleLength):
			pass
		if vehicle.mode == VehicleMode("RTL"):
			vehicle_flying = False
		emg = emg.reshape(1, emg.shape[0], emg.shape[1])
		prediction = model.predict_classes(emg)
		print('['+str(prediction[0])+']: '+gesture_names[prediction[0]])	
		
		if(gesture_names[prediction[0]]=='Rest'):
			pass
		elif(gesture_names[prediction[0]]=='Fist'):
			# Go Down
			send_ned_velocity(vehicle, 0, 0, gnd_speed)
		elif(gesture_names[prediction[0]]=='Hold_Left'):
			# Tilt Left
			send_ned_velocity(vehicle, -gnd_speed, 0, 0)
		elif(gesture_names[prediction[0]]=='Hold_Right'):
			# Tilt Right
			send_ned_velocity(vehicle, gnd_speed, 0, 0)
		elif(gesture_names[prediction[0]]=='Flower'):
			# Move Back
			send_ned_velocity(vehicle, 0, -gnd_speed, 0)
		elif(gesture_names[prediction[0]]=='Finger_Spread'):
			# Go Up
			send_ned_velocity(vehicle, 0, 0, -gnd_speed)
		elif(gesture_names[prediction[0]]=='Metal'):
			# Move Forward
			send_ned_velocity(vehicle, 0, gnd_speed, 0)
		elif(gesture_names[prediction[0]]=='Thumbs_Up'):
			if not vehicle_flying:
				arm_and_takeoff(vehicle, 10)
				if vehicle.armed:
					vehicle_flying=True
		elif(gesture_names[prediction[0]]=='Peace'):
			print("Returning drone to launch")
			vehicle.mode = VehicleMode("RTL")
			vehicle_flying = False
