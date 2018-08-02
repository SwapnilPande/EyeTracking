from socketIO_client_nexus import SocketIO, LoggingNamespace
import json
from keras.models import Model, load_model
from iTrackerUI import iTrackerUI #Importing UI object
import numpy as np
import cv2
import time, datetime
from imageUtils import normalize
#Importing execution parameters
with open('predict_param.json') as f: #Open paramter file
	paramJSON = json.load(f) #Load JSON as dict


######################################## UI Definition ########################################
#Initializing UI Object
print("Initializing UI")
ui = iTrackerUI()

# updateUI
# Calls the update function for pygame ui to redraw cursor at updated gze location
# arguments:
# 	gazePrediction - tuple containing (x,y) estimate of gaze location relative to camera
def updateUI(gazePrediction):
	ui.updateUI(gazePrediction)


####################### Machine Learning Model & Tensorflow Definitions #######################
#Path to the trained model
print()
print("Loading trained iTracker Model")
modelPath = paramJSON['prexistingModelPath']
model = load_model(modelPath) 
model.load_weights(modelPath)


# getFaceGrids
# Extract the faceGrid information from JSON to numpy array
# Arguments:
# 	fgMetadata - dictionary containing metadata about facegrid 	
# Returns a numpy array containing teh facegrids of length 625
def getFaceGrid(fgMetadata):
	#Size of the facegrid output
	faceGridSize = 625

	#Retrieve necessary values
	x =  fgMetadata['X']
	y =  fgMetadata['Y']
	w =  fgMetadata['W']
	h =  fgMetadata['H']

	#Create 5x5 array of zeros
	faceGrid = np.zeros((25, 25))

	#Write 1 in the FaceGrid for location of face
	#Subtracting 1 in range because facegrid is 1 indexed
	xBound = x-1+w
	yBound = y-1+h

	if(x < 0): #Flooring x & y to zero
		x = 0 
	if(y < 0):
		y = 0
	if(xBound > 25): #Capping maximum value of x & y to 25
		xBound = 25
	if(yBound > 25):
		yBound = 25

	for i in range(x-1,xBound):
		for j in range(y-1,yBound):
			faceGrid[j][i] = 1
	#Reshape facegird from 25x25 to 625x1
	faceGrid = np.reshape(faceGrid, faceGridSize)

	return faceGrid

# import argparse #Argument parsing

# parser = argparse.ArgumentParser()
# parser.add_argument("execution_name", help="Name to identify the train execution - used to name the log files")
# parser.add_argument("-d", "--default", help="Use default options when configuring execution", action='store_true')
# args = parser.parse_args()

# import processData

# with open('ml_param.json') as f: #Open paramter file
# 	paramJSON2 = json.load(f) #Load JSON as dict
# #Load Data paths
# dataPathJSON = paramJSON2['dataPaths']
# pathToData = dataPathJSON['pathToData']
# pathTemp = dataPathJSON['pathToTempDir']

# processData.initializeData(pathToData, pathTemp, 0.8, 0.15, args)

# ppTrain = processData.DataPreProcessor(pathToData, pathTemp, 1, 'test', args, loadAllData = False)
def predictGaze(data):
	start = time.time()
	frameData = json.loads(data)
	prediction = None # Initializing prediction object
	#Checking if incoming data is valid
	if(frameData['frameInfo']['faceGrid']['IsValid']*
		frameData['frameInfo']['face']['IsValid']*
		frameData['frameInfo']['leftEye']['IsValid']*
		frameData['frameInfo']['rightEye']['IsValid'] == 1):

		#Extracting numpy arrays from string
		#They are 1D at first and need to be reshaped
		face = normalize(cv2.imdecode(np.asarray(frameData['Image']['face']['data'], dtype = np.int8), -1), 255)
		leftEye = normalize(cv2.imdecode(np.asarray(frameData['Image']['leftEye']['data'], dtype=np.uint8), -1), 255)
		rightEye = normalize(cv2.imdecode(np.asarray(frameData['Image']['rightEye']['data'], dtype=np.uint8), -1), 255)

		###TEST CODE
		#cv2.destroyAllWindows()
		# cv2.imshow("Face",face)
		#cv2.imshow('e',rightEye)
		# #cv2.imshow(rightEye)
		#cv2.waitKey(0)

		#Generate facegrid from metadata
		faceGrid = getFaceGrid(frameData['frameInfo']['faceGrid'])
		#Creaing input dictionary to pass to model
		# for input, label in ppTrain:
		# 	prediction = model.predict(input)[0]
		# 	print(str(prediction) + ' ' + str(label))
		predictionInput = {
					'input_3' : np.expand_dims(face,axis=0), 
					'input_1' : np.expand_dims(leftEye,axis=0), 
					'input_2' : np.expand_dims(rightEye,axis=0), 
					'input_4' : np.expand_dims(faceGrid, axis=0)
					}
		prediction = model.predict(predictionInput)[0]
		delta = (prediction[0] - frameData['frameInfo']['dotInfo']['XCam'], prediction[1] - frameData['frameInfo']['dotInfo']['YCam'])
		end = time.time()
		print( 1/(end-start))

		print(delta)
		updateUI(delta)
	#else:
		#print("Invalid Data")
	#updateUI(prediction)


#################################### SocketIO Definitions #####################################
def on_connect():
    print('Connected')

def on_disconnect():
    print('Disconnected')

def on_reconnect():
    print('Reconnected')

#Passes receeived frame data to predictGaze function to genreate predicted gaze location
def frameReceived(data):
	#print("Received Frame")
	predictGaze(data)

#Parameters for connecting to server sending OpenPose data
ipAddress = paramJSON['dataStreamServerAddress']
port = paramJSON['dataStreamServerPort']

#Initialize SocketIO Server
print()
print("Starting SocketIO Client")
socketIO = SocketIO(ipAddress, port, LoggingNamespace)

#Standard definitions for connection events
socketIO.on('connect', on_connect)
socketIO.on('disconnect', on_disconnect)
socketIO.on('reconnect', on_reconnect)

#Definition for frame received events, called frameReceived function to update UI
socketIO.on('frame', frameReceived)

#Wait for incoming messages
socketIO.wait()




