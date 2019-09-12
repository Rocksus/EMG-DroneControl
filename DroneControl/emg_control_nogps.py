#!/usr/bin/env python

"""
set_attitude_target.py: (Copter Only)
This example shows how to move/direct Copter and send commands
 in GUIDED_NOGPS mode using DroneKit Python.
Caution: A lot of unexpected behaviors may occur in GUIDED_NOGPS mode.
		Always watch the drone movement, and make sure that you are in dangerless environment.
		Land the drone as soon as possible when it shows any unexpected behavior.
Tested in Python 2.7.10
"""

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode ')
parser.add_argument('--connect',
				   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

def arm_and_takeoff_nogps(aTargetAltitude):
	"""
	Arms vehicle and fly to aTargetAltitude without GPS data.
	"""

	##### CONSTANTS #####
	DEFAULT_TAKEOFF_THRUST = 0.7
	SMOOTH_TAKEOFF_THRUST = 0.6

	print("Basic pre-arm checks")
	# Don't let the user try to arm until autopilot is ready
	# If you need to disable the arming check,
	# just comment it with your own responsibility.
	# while not vehicle.is_armable:
	#     print(" Waiting for vehicle to initialise...")
	#     time.sleep(1)


	print("Arming motors")
	# Copter should arm in GUIDED_NOGPS mode
	vehicle.mode = VehicleMode("GUIDED_NOGPS")
	vehicle.armed = True

	while not vehicle.armed:
		print(" Waiting for arming...")
		vehicle.armed = True
		time.sleep(1)

	print("Taking off!")

	thrust = DEFAULT_TAKEOFF_THRUST
	while True:
		current_altitude = vehicle.location.global_relative_frame.alt
		print(" Altitude: %f  Desired: %f" %
			  (current_altitude, aTargetAltitude))
		if current_altitude >= aTargetAltitude*0.95: # Trigger just below target alt.
			print("Reached target altitude")
			break
		elif current_altitude >= aTargetAltitude*0.6:
			thrust = SMOOTH_TAKEOFF_THRUST
		set_attitude(thrust = thrust)
		time.sleep(0.2)

def send_attitude_target(roll_angle = 0.0, pitch_angle = 0.0,
						 yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
						 thrust = 0.5):
	"""
	use_yaw_rate: the yaw can be controlled using yaw_angle OR yaw_rate.
				  When one is used, the other is ignored by Ardupilot.
	thrust: 0 <= thrust <= 1, as a fraction of maximum vertical thrust.
			Note that as of Copter 3.5, thrust = 0.5 triggers a special case in
			the code for maintaining current altitude.
	"""
	if yaw_angle is None:
		# this value may be unused by the vehicle, depending on use_yaw_rate
		yaw_angle = vehicle.attitude.yaw
	# Thrust >  0.5: Ascend
	# Thrust == 0.5: Hold the altitude
	# Thrust <  0.5: Descend
	msg = vehicle.message_factory.set_attitude_target_encode(
		0, # time_boot_ms
		1, # Target system
		1, # Target component
		0b00000000 if use_yaw_rate else 0b00000100,
		to_quaternion(roll_angle, pitch_angle, yaw_angle), # Quaternion
		0, # Body roll rate in radian
		0, # Body pitch rate in radian
		math.radians(yaw_rate), # Body yaw rate in radian/second
		thrust  # Thrust
	)
	vehicle.send_mavlink(msg)

def set_attitude(roll_angle = 0.0, pitch_angle = 0.0,
				 yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
				 thrust = 0.5):
	"""
	Note that from AC3.3 the message should be re-sent more often than every
	second, as an ATTITUDE_TARGET order has a timeout of 1s.
	In AC3.2.1 and earlier the specified attitude persists until it is canceled.
	The code below should work on either version.
	Sending the message multiple times is the recommended way.
	"""
	send_attitude_target(roll_angle, pitch_angle,
						 yaw_angle, yaw_rate, False,
						 thrust)
	# start = time.time()
	# while time.time() - start < duration:
	send_attitude_target(roll_angle, pitch_angle,
						 yaw_angle, yaw_rate, False,
						 thrust)

def to_quaternion(roll = 0.0, pitch = 0.0, yaw = 0.0):
	"""
	Convert degrees to quaternions
	"""
	t0 = math.cos(math.radians(yaw * 0.5))
	t1 = math.sin(math.radians(yaw * 0.5))
	t2 = math.cos(math.radians(roll * 0.5))
	t3 = math.sin(math.radians(roll * 0.5))
	t4 = math.cos(math.radians(pitch * 0.5))
	t5 = math.sin(math.radians(pitch * 0.5))

	w = t0 * t2 * t4 + t1 * t3 * t5
	x = t0 * t3 * t4 - t1 * t2 * t5
	y = t0 * t2 * t5 + t1 * t3 * t4
	z = t1 * t2 * t4 - t0 * t3 * t5

	return [w, x, y, z]

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
	connection_string = args.connect
	sitl = None
	gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

	myo.init(sdk_path='../myo-sdk-win-0.9.0')
	hub = myo.Hub()
	listener = Listener()

	# Start SITL if no connection string specified
	if not connection_string:
		import dronekit_sitl
		sitl = dronekit_sitl.start_default()
		connection_string = sitl.connection_string()

	# Load Model
	model = load_model('../32_Length_Sample_64_64_32.h5')

	# View summary of model
	model.summary()

	# Connect to the Vehicle
	print('Connecting to vehicle on: %s' % connection_string)
	vehicle = connect(connection_string, wait_ready=True)

	while hub.run(listener.on_event, 500):
		emg = np.array(listener.get_emg_data())
		while(len(emg)<sampleLength):
			pass
		
		emg = emg.reshape(1, emg.shape[0], emg.shape[1])
		prediction = model.predict_classes(emg)
		print('['+str(prediction[0])+']: '+gesture_names[prediction[0]])	
		if vehicle.mode == VehicleMode("LAND"):
			vehicle_flying = False

		if(gesture_names[prediction[0]]=='Rest'):
			# Reset attitude, or it will persist for 1s more due to the timeout
			send_attitude_target(0, 0,
								 0, 0, True,
								 thrust)
			pass
		elif(gesture_names[prediction[0]]=='Fist'):
			# Go Down
			set_attitude(thrust=-0.5)
		elif(gesture_names[prediction[0]]=='Hold_Left'):
			# Tilt Left
			set_attitude(roll_angle = 5, thrust = 0.5, duration = 3.21)
		elif(gesture_names[prediction[0]]=='Hold_Right'):
			# Tilt Right
			set_attitude(roll_angle = -5, thrust = 0.5, duration = 3.21)
		elif(gesture_names[prediction[0]]=='Flower'):
			# Move Back
			set_attitude(pitch_angle = 5, thrust = 0.5, duration = 3.21)
		elif(gesture_names[prediction[0]]=='Finger_Spread'):
			# Go Up
			set_attitude(thrust=0.5)
		elif(gesture_names[prediction[0]]=='Metal'):
			# Move Forward		
			set_attitude(pitch_angle = -5, thrust = 0.5, duration = 3.21)
		elif(gesture_names[prediction[0]]=='Thumbs_Up'):
			if not vehicle_flying:
				arm_and_takeoff(vehicle, 10)
				if vehicle.armed:
					vehicle_flying=True
		elif(gesture_names[prediction[0]]=='Peace'):
			print("Landing Mode")
			vehicle.mode = VehicleMode("LAND")
			vehicle_flying = False

	# Shut down simulator if it was started.
	if sitl is not None:
		sitl.stop()
		
	print("FINISHED")

