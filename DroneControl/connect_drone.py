from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil


def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
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


    # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

if __name__ == '__main__':
	#serial port for drone
	connection_string = 'udp:127.0.0.1:14551'

	#connect to drone, receive vehicle object
	vehicle = connect(connection_string, wait_ready=True)

	# Get some vehicle attributes (state)
	print ("Get some vehicle attribute values:")
	print (" GPS: %s" % vehicle.gps_0)
	print (" Battery: %s" % vehicle.battery)
	print (" Last Heartbeat: %s" % vehicle.last_heartbeat)
	print (" Is Armable?: %s" % vehicle.is_armable)
	print (" System status: %s" % vehicle.system_status.state)
	print (" Mode: %s" % vehicle.mode.name)    # settable


	vehicle.close()