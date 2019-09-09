from __future__ import print_function
from myo.utils import TimeInterval
import myo
import inspect
import sys
import keyboard
import matplotlib.pyplot as plt
import os
import numpy as np
import time

from threading import Lock, Thread
from collections import deque

space_pressed = False
#iteration of training
train_iter = 5

class Listener(myo.DeviceListener):

	def __init__(self):
		self.orientation = None
		self.emg = None
		self.pose = myo.Pose.rest
		self.record_emg = False
		self.lock = Lock()
		self.disabled = True
		self.emg_data = None

	def get_emg_array(self):
		return self.emg_data

	def enable_emg(self, status):
		self.record_emg = status 
		if status is True:
			self.emg_data = []

	def on_connected(self, event):
		print("{} successfully connected!".format(event.device_name))
		event.device.vibrate(myo.VibrationType.medium)
		#Allow EMG Streaming
		event.device.stream_emg(True)
		train_ready = True
		self.disabled = False

	def on_emg(self, event):
		self.emg = event.emg
		if(self.record_emg):
			self.emg_data.append(self.emg)

if __name__ == '__main__':
	myo.init(sdk_path='myo-sdk-win-0.9.0')
	hub = myo.Hub()
	listener = Listener()
	with hub.run_in_background(listener.on_event):
		#Ensures myo is ready before trying to work with data
		while listener.disabled:
			pass

		gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

		for gesture in gesture_names:
			try:
				os.makedirs('Gestures/'+gesture)
				print('Successfully created training folder for '+gesture)
			except:
				pass
			files = []
			# r=root, d=directories, f = files
			for r, d, f in os.walk('Gestures/'+gesture):
				for file in f:
					if '.csv' in file:
						files.append(file)

			last_number = len(files)+1
			print('==========================================')
			print('Ready to train data for gesture: '+gesture)
			print('==========================================')

			for i in range(train_iter):
				print('Iteration '+str(i)+':')
				print('Hold space to start recording....')
				#wait until space is pressed
				while not keyboard.is_pressed('space'):
					pass
				print('Recording data... Release to stop')
				#remove overhead
				time.sleep(0.2)
				listener.enable_emg(True)
				#execute data recording during key pressed
				while keyboard.is_pressed('space'):
					pass 

				#finish the data recording
				print('Released')
				listener.enable_emg(False)
				emg_array = listener.get_emg_array()
				emg_display = np.array(emg_array).T
				# print(emg_array)

				fig, ax = plt.subplots(nrows=8, ncols=1)
				
				fig.canvas.set_window_title(gesture+' iter '+str(i))
				for row, j in zip(ax, range(8)):
					row.set_ylim(top=100)
					row.set_ylim(bottom=-100)
					row.plot(emg_display[j])

				plt.show()

				np.savetxt('Gestures/'+gesture+'/'+gesture+'_'+str(last_number)+'.csv', emg_array ,delimiter=',')
				last_number = last_number + 1