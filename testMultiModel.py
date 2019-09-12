from keras.models import load_model
import numpy as np
import os
from keras.utils import np_utils, plot_model
import matplotlib.pyplot as plt
import csv

sampleLength = 32
printToBash = True

def createCNNLSTM(cnn1, cnn2, lstm):
	model = Sequential()
	if(cnn1>0):
		model.add(Conv1D(cnn1, kernel_size=3, activation='relu', input_shape = (sampleLength, 8)))
		model.add(Dropout(rate=0.5))
	if(cnn2>0):
		model.add(Conv1D(cnn2, kernel_size=3, activation='relu'))
		model.add(Dropout(rate=0.5))
	if(lstm>0):
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

model_nodes = ['32_length_Sample_32cnn', '32_length_sample_64cnn', '32_length_sample_128cnn','32_length_sample_32_32cnn', '32_length_sample_16lstm','32_length_sample_32lstm','32_length_sample_64lstm', '32_Length_Sample_32_32_16', '32_Length_Sample_64_32_16', '32_Length_Sample_64_64_32', '32_Length_Sample_128_64_32']

# Empty variable to contain array of models
models = []

# Load all model
for model in model_nodes:
	models.append(load_model(model+'.h5'))

# Singular Classification for each model
gestureX = []
classification = 0
classificationRange = 1000

false_positive = []
for i in range(len(gesture_names)):
	false_positive.append([])

for gesture in gesture_names:
	for r, d, f in os.walk('Gestures/'+gesture):
		gesture_x = []
		for file in f:
			if '.csv' in file:
				# data = pd.read_csv('Gestures/'+gesture+'/'+file)
				data = np.genfromtxt('Gestures/'+gesture+'/'+file, delimiter=',')
				fileX = []
				length = 0
				for x in data:
					# if(len(gesture_x)<classificationRange):
					if(length>=sampleLength):
						gesture_x.append(fileX)
						fileX = []
						length=0
					fileX.append(np.asarray(x))
					length = length + 1
				# Stack the list of numpy arrays
		k = np.arange(len(gesture_x))
		k = np.random.choice(k, 1000)
		newX = []
		for i in k:
			newX.append(gesture_x[i])
		gestureX.append(newX)
		for i in range(len(gesture_names)):
			if not i is classification:
				kk = np.arange(len(gesture_x))
				kk = np.random.choice(kk, 200)
				for j in kk:
					false_positive[i].append(gesture_x[j])
	classification = classification + 1

model_acc = []
# Iterate through each model
csv_data = []
for model, model_profile in zip(models,model_nodes):
	# Get classification Predictions
	csv_d = []
	if(printToBash):
		print('==========Classification Data for model_profile: ' + model_profile +'==========')
	csv_d.append(model_profile)
	acc_gestures = []
	# Iterate through each gesture
	# Also provide false positive data to test
	for gesture, gestureName, fp in zip(gestureX, gesture_names, false_positive):
		count = 0
		for datas in gesture:
			data = np.array(datas)
			data = data.reshape(1, data.shape[0], data.shape[1])
			prediction = model.predict_classes(data)
			if(gesture_names[prediction[0]]==gestureName):
				count=count+1
		acc = count/len(gesture) * 100
		if(printToBash):
			print('Gesture (' + gestureName + '): '  + str(acc)+'%')
		csv_d.append(acc)
		count = 0
		for datas in fp:
			data = np.array(datas)
			data = data.reshape(1, data.shape[0], data.shape[1])
			prediction = model.predict_classes(data)
			if (gesture_names[prediction[0]]==gestureName):
				count=count+1
		fpCount = count/len(fp) * 100
		if(printToBash):
			print('False Positive (' + gestureName + '): '  + str(fpCount)+'%')
		csv_d.append(fpCount)
		acc_gestures.append(acc)
	model_acc.append(acc_gestures)
	if(len(csv_d)>0):
		csv_data.append(csv_d)

with open('modelResults.csv', 'w') as csvFile:
	writer = csv.writer(csvFile)
	writer.writerows(csv_data)

csvFile.close()
#write the model accuracy
