import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Conv1D, Flatten
import os
from keras.utils import np_utils, plot_model
import matplotlib.pyplot as plt

sampleLength = 32

def createCNNLSTM(cnn1, cnn2, lstm):
	model = Sequential()
	model.add(Conv1D(cnn1, kernel_size=3, activation='relu', input_shape = (sampleLength, 8)))
	model.add(Dropout(rate=0.5))
	model.add(Conv1D(cnn2, kernel_size=3, activation='relu'))
	model.add(Dropout(rate=0.5))
	# model.add(Dense(32, activation='relu', input_shape=(8,)))
	# model.add(Dense(32, activation='relu'))
	# model.add(Dropout(0.5))
	model.add(LSTM(lstm, return_sequences=True))
	model.add(Flatten())
	model.add(Dense(num_gestures, activation='softmax'))
	return model

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
trainY = np_utils.to_categorical(trainY)

# Shuffle data to remove overfitting
trainX, trainY = shuffleData(trainX, trainY)

model_nodes = ['32_Length_Sample_32_32_16', '32_Length_Sample_64_32_16', '32_Length_Sample_64_64_32', '32_Length_Sample_128_64_32', '48_Length_Sample_32_32_16', '48_Length_Sample_64_32_16', '48_Length_Sample_64_64_32', '48_Length_Sample_128_64_32']

# Empty variable to contain array of models
models = []
models.append(createCNNLSTM(32,32,16))
models.append(createCNNLSTM(64,32,16))
models.append(createCNNLSTM(64,64,32))
models.append(createCNNLSTM(128,64,32))

histories = []
for model in models:
	model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
	history = model.fit(trainX, trainY,validation_split=0.33, epochs=225, batch_size=32, shuffle=True)
	histories.append(history)

for history, savefile in zip(histories, model_nodes):
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

	plt.savefig(savefile+'.png')
	plt.clf()
	plt.cla()
	plt.close()
	# Add train per gesture here

# Singular Classification for each model
gestureX = []
classification = 0
classificationRange = 1000

for gesture in gesture_names:
	for r, d, f in os.walk('Gestures/'+gesture):
		gesture_x = []
		gesture_y = []
		for file in f:
			if '.csv' in file:
				# data = pd.read_csv('Gestures/'+gesture+'/'+file)
				data = np.genfromtxt('Gestures/'+gesture+'/'+file, delimiter=',')
				fileX = []
				length = 0
				for x in data:
					if(len(gesture_x)<classificationRange):
						if(length>=sampleLength):
							gesture_x.append(fileX)
							fileX = []
							length=0
						fileX.append(np.asarray(x))
						length = length + 1
				# Stack the list of numpy arrays
		gestureX.append(gesture_x)
	classification = classification + 1


model_acc = []
for model, model_profile in zip(models,model_nodes):
	# Get classification Predictions
	print('Classification Data for model_profile: ' + model_profile)
	acc_gestures = []
	for gesture, gestureName in zip(gestureX, gesture_names):
		count = 0
		for datas in gesture:
			data = np.array(datas)
			data = data.reshape(1, data.shape[0], data.shape[1])
			prediction = model.predict_classes(data)
			if(gesture_names[prediction[0]]==gestureName):
				count=count+1
		acc = count/classificationRange * 100
		print('Gesture (' + gestureName + '): '  + str(acc)+'%')
		acc_gestures.append(acc)
	model_acc.append(acc_gestures)

#write the model accuracy