import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Conv1D, Flatten
import os
from keras.utils import np_utils, plot_model
import matplotlib.pyplot as plt

sampleLength = 32

def shuffleData(in_x, in_y):
	newTrainX = []
	newTrainY = []
	dataLen = len(in_x)
	k = np.arange(dataLen)
	np.random.shuffle(k)
	for i in k:
		newTrainX.append(in_x[i])
		newTrainY.append(in_y[i])
	newTrainX = np.stack(newTrainX, axis = 0)
	newTrainY = np.stack(newTrainY, axis = 0)
	return newTrainX, newTrainY

#get training data directories by pre-determined gestures
gesture_names = ['Rest', 'Fist', 'Hold_Left', 'Hold_Right', 'Flower', 'Finger_Spread','Metal','Thumbs_Up','Peace']

#get number of outputs
num_gestures = len(gesture_names)

#Input data
trainX = []
#Output Class
trainY = []

#load data
classification = 0
for gesture in gesture_names:
	for r, d, f in os.walk('Gestures/'+gesture):
		for file in f:
			if '.csv' in file:
				# data = pd.read_csv('Gestures/'+gesture+'/'+file)
				data = np.genfromtxt('Gestures/'+gesture+'/'+file, delimiter=',')
				fileX = []
				length = 0
				for x in data:
					if(length>=sampleLength):
						trainX.append(fileX)
						trainY.append(classification)
						fileX = []
						length=0
					fileX.append(np.asarray(x))
					length = length + 1
				# Stack the list of numpy arrays
	classification = classification + 1

trainX = np.stack(trainX, axis=0)


# Normalize data to 0 1 analog

# Here, x.ptp(0) returns the "peak-to-peak" 
# (i.e. the range, max - min) along axis 0. 
# This normalization also guarantees that the 
# minimum value in each column will be 0.
# trainX = (trainX - trainX.min(0)) / trainX.ptp(0)
trainY = np_utils.to_categorical(trainY)

# Shuffle data to remove overfitting
trainX, trainY = shuffleData(trainX, trainY)

# setup model
# create and fit the LSTM network
model = Sequential()
model.add(Conv1D(64, kernel_size=3, activation='relu', input_shape = (sampleLength, 8)))
model.add(Dropout(rate=0.5))
model.add(Conv1D(32, kernel_size=3, activation='relu'))
model.add(Dropout(rate=0.5))
# model.add(Dense(32, activation='relu', input_shape=(8,)))
# model.add(Dense(32, activation='relu'))
# model.add(Dropout(0.5))
model.add(LSTM(16, return_sequences=True))
model.add(Flatten())
model.add(Dense(num_gestures, activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history= model.fit(trainX, trainY,validation_split=0.33, epochs=225, batch_size=16, shuffle=True)

# Plot training & validation accuracy values
# Create 2 subplots
plt.subplot(2, 1, 1)

# Subplot for model accuracy
plt.title('Model Accuracy')
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')

# Subplot for model loss
plt.subplot(2,1,2)
plt.title('Model Loss')
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')

plt.tight_layout()

# Save model to file for testing
model.save('EMG_Model_CNN_RNN.h5')

plt.show()