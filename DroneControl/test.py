import time
from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil
import keyboard
import myo

def toEuler(quat):
    quat = quat[0]

    # Roll
    sin = 2.0 * (quat.w * quat.w + quat.y * quat.z)
    cos = +1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y)
    roll = math.atan2(sin, cos)

    # Pitch
    pitch = math.asin(2 * (quat.w * quat.y - quat.z * quat.x))

    # Yaw
    sin = 2.0 * (quat.w * quat.z + quat.x * quat.y)
    cos = +1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z)
    yaw = math.atan2(sin, cos)
    return [pitch, roll, yaw]

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


class Listener(myo.DeviceListener):

  def __init__(self):
    self.orientation = None
    self.pose = myo.Pose.rest
    self.emg_enabled = False
    self.locked = False
    self.rssi = None
    self.emg = None

  def on_connected(self, event):
  	print('Connected to Myo!')
    # event.device.stream_emg(True)
    # self.emg_enabled = True

  def on_pose(self, event):
    self.pose = event.pose

  def on_emg(self, event):
    self.emg = event.emg


if __name__ == '__main__':
	connection_string = 'udp:127.0.0.1:14551'

	print('Connecting...')
	
	# Setup the command flying speed
	gnd_speed = 2 # m/s
	myo.init(sdk_path='../myo-sdk-win-0.9.0')
	hub = myo.Hub()
	listener = Listener()

	with hub.run_in_background(listener.on_event):
		# vehicle = connect(connection_string, baud=57600, wait_ready=True)
		vehicle = connect('com19', wait_ready=True)
		vehicle.mode = VehicleMode("STABILIZE")
		vehicle.armed = True
		vehicle.flush()

		arm_and_takeoff(vehicle, 10)

		while 1:
			if(listener.pose == myo.Pose.wave_in):
				print("Myo send backward")
				send_ned_velocity(vehicle, 0, -gnd_speed, 0)
			elif(listener.pose == myo.Pose.wave_out):
				print("Myo send forward")
				send_ned_velocity(vehicle, 0, gnd_speed, 0)
			elif(keyboard.is_pressed('up')):
				print("Sending Forward Signal")
				send_ned_velocity(vehicle, gnd_speed, 0, 0)
			elif(keyboard.is_pressed('down')):
				print("Sending Backward signal")
				send_ned_velocity(vehicle, -gnd_speed, 0, 0)
			elif(keyboard.is_pressed('left')):
				print("Sending left signal")
				send_ned_velocity(vehicle, 0, -gnd_speed, 0)
			elif(keyboard.is_pressed('right')):
				print("Sending right signal")
				send_ned_velocity(vehicle, 0, gnd_speed, 0)
			elif(keyboard.is_pressed('u')):
				print("Sending up signal")
				send_ned_velocity(vehicle, 0, 0, -gnd_speed)
			elif(keyboard.is_pressed('j')):
				print("Sending down signal")
				send_ned_velocity(vehicle, 0, 0, gnd_speed)
			elif(keyboard.is_pressed('r')):
				print("Returning drone to launch")
				vehicle.mode = VehicleMode("RTL")
			time.sleep(1)