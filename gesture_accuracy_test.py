from keras.models import load_model
from collections import deque
import numpy as np
import os

if __name__ == '__main__':
	model = load_model('EMG_Model_CNN_RNN.h5')

	model.summary()

	gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

	for gesture in gesture_names:
		files = []
		for r,d,f in os.walk('Gestures/'+gesture):
			for file in f:
				if '.csv' in file:
					files.append(file)