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
# Root Mean Square
def rms(array):
    n = len(array)
    sum = 0
    for a in array:
        sum =+ a*a
    return np.sqrt((1/float(n))*sum)

# Integrated Absolute Value
def iav(array):
    sum = 0
    for a in array:
        sum += np.abs(a)
    return sum

# Simple Square Integral
def ssi(array):
    sum = 0
    for a in array:
        sum += a*a
    return sum

# Variance
def var(array):
    n = len(array)
    sum = 0
    for a in array:
        sum += a*a
    return ((1/float(n-1))*sum)

# Waveform Length
def wl(array):
    sum = 0
    for a in range(0,len(array)-1):
        sum =+ array[a+1] - array[a]
    return sum

# Average Amplitude Change
def aac(array):
    n = len(array)
    sum = 0
    for a in range(0,n-1):
        sum =+ array[0+1] - array[0]
    return sum/float(n)


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

print(trainX.shape)
print(trainY.shape)
print(trainX)
# setup model
# create and fit the LSTM network
model = Sequential()
model.add(Conv1D(64, kernel_size=3, activation='relu', input_shape = (sampleLength, 8)))
model.add(Dropout(rate=0.7))
model.add(Conv1D(64, kernel_size=3, activation='relu'))
model.add(Dropout(rate=0.7))
# model.add(Dense(32, activation='relu', input_shape=(8,)))
# model.add(Dense(32, activation='relu'))
# model.add(Dropout(0.5))
model.add(LSTM(32, return_sequences=True))
model.add(Flatten())
model.add(Dense(num_gestures, activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history= model.fit(trainX, trainY,validation_split=0.33, epochs=150, batch_size=16, shuffle=True)

# Plot training & validation accuracy values
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

model.save('EMG_Model_CNN_RNN.h5')

