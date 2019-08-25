# Import Classes
from keras.models import load_model
from collections import deque
import myo
import numpy as np

sampleLength = 48

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


#Init main
if __name__ == '__main__':
	#Load Model
	model = load_model('EMG_Model_CNN_RNN.h5')

	# Summarize Model
	model.summary()

	# Initialize myo
	myo.init(sdk_path='myo-sdk-win-0.9.0')
	hub = myo.Hub()
	listener = Listener()
	gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

	while hub.run(listener.on_event, 500):
		emg = np.array(listener.get_emg_data())
		# Ensure data queue is ready
		while(len(emg)<sampleLength):
			pass
		emg = emg.reshape(1, emg.shape[0], emg.shape[1])
		prediction = model.predict_classes(emg)

		print('['+str(prediction[0])+']: '+gesture_names[prediction[0]])