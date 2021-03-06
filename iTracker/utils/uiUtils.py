#uiUtils contains definitions for user interface utilities 
#Abstracts these functions so that it is not needed to import libraries in each file

from progressbar import ProgressBar
# yesNoPrompt
# Accepts a yes or no (y/n) input from the user and returns a boolean with result
def yesNoPrompt(useDefault, default):
	if(useDefault):
		response = default
		print(default)
	else:
		response = input()
	while(response.lower() != 'y' and response.lower() != 'n'):
		print("Enter only y or n:")
		response = input()
	return (response == 'y')

# listOptionsPrompt
# Accepts a number input to select an option from a list
# 
def listOptionsPrompt(options):
	selection = None
	for i, option in enumerate(options):
		print(str(i+1) + ": " + str(option))
	response = input()
	while True:
		try:
			selection = int(response)
			if(selection > 0 and selection <= len(options)):
				break
		except:
			pass
		print("Enter a selection between 1 and " + str(len(options)))
		response = input()
	return options[selection-1]

# createProgress Bar
# Initializes a progress bar object with an optional max value
# maxVal - Optional max value for progress bar
# 			If no maxVal is passed, progressBar will be initialized without max
# Returns ProgressBar Object
def createProgressBar(maxVal = None):
	if(maxVal != None):
		return ProgressBar(maxval = maxVal)
	return ProgressBar()


class iTrackerUI:
	

	#Creates the nececssary pygame UI elements to draw the UI for iTracker
	def __init__(self):
		#Imports when class is instantiated
		self.ctypes = __import__('ctypes')
		self.sys =  __import__('sys')
		self.os = __import__('os')
		self.pygame = __import__('pygame')

		if self.os.name == 'nt':
			self.ctypes.windll.user32.SetProcessDPIAware()

		#Initializing pygame UI
		self.pygame.init()

		self.dispInfo = self.pygame.display.Info() #Collecting info about the display application is running on
		self.screenSize = self.wScreenPx, self.hScreenPx = (self.dispInfo.current_w, self.dispInfo.current_h) #Storing screen size from info object
		self.black = 0,0,0 #Black tuple for writing background color

		#Define camera and screen parameters
		self.xCameraOffsetCm = 14.25 #Horizonatl displacement of camera relative to origin pixel in cm
		self.yCameraOffsetCm = -0.75 #Vertical displacement of camera relative to origin pixel in centimeters
		self.wScreenCm = 28.875 #Width of the screen in cm
		self.hScreenCm = 19.25 #Height of the screen in cm

		#Create screen surface object to display
		self.screen = self.pygame.display.set_mode(self.screenSize, self.pygame.FULLSCREEN)

		#Conversion factors to scale centimeters to screen pixels
		self.xCm2Px = self.wScreenPx/self.wScreenCm
		self.yCm2Px = self.hScreenPx/self.hScreenCm

		self.clock = self.pygame.time.Clock() #Initialize clock for calculating fps
		self.font = self.pygame.font.Font(None, 60) #Create font for writing fps on screen



	# cm2Px
	# Transforms x and y coordinates in centimeters (relative to camera) to pixels (relative to origin pixel)
	# Arugments:
	# 	coods - tuple containing coordinates in centimeters relative to camera
	# Returns tuple containing transformed coordinates relative to origin pixel (and graphics coordinate system)
	def cm2Px(self, coords):
		return (round(self.xCm2Px*(coords[0] + self.xCameraOffsetCm) - self.cursorSize[0]/2),
				round(self.yCm2Px*(-1*coords[1] + self.yCameraOffsetCm) - self.cursorSize[1]/2))

	# updateCursor
	# Redraws the UI with the updated cursor location
	# updatedCursorCoords - tuple containing x and y coordinates of the cursor
	# If no coordinates are passed, display is updated with previous cursor coordinates
	def updateUI(self):
		#Looks for exit event to close application
		for event in self.pygame.event.get():
			if event.type == self.pygame.QUIT: self.sys.exit()

		#Update screen
		self.pygame.display.flip()

class liveUI(iTrackerUI):

	def __init__(self):
		super(liveUI, self).__init__()

		#Load image for dots and cursor and scale to 100x100 pixels
		self.dotSize = (100,100)
		self.cursorSize = (100,100)
		self.dot = self.pygame.transform.scale(self.pygame.image.load("UI_assets/pokeball.png"), self.dotSize) 
		self.cursor = self.pygame.transform.scale(self.pygame.image.load("UI_assets/greatball.png"), self.cursorSize) 	

		#Generating coordinates for dots on screen relative to screen size
		self.x1 = int(self.wScreenPx*0.25 - self.dotSize[0]/2) 
		self.x2 = int(self.wScreenPx*0.75 - self.dotSize[0]/2)
		self.y1 = int(self.hScreenPx*0.25 - self.dotSize[1]/2)
		self.y2 = int(self.hScreenPx*0.75 - self.dotSize[1]/2)

		self.dotCoords = [(self.x1, self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)]

	def updateUI(self, updatedCursorCoords):
		#Clears the screen to draw update
		self.screen.fill(self.black)

		#Draw dots on screen
		for dotCoord in self.dotCoords:
			self.screen.blit(self.dot, dotCoord)
		
		#Store updated cursor coordinates
		self.cursorCoords = super().cm2Px(updatedCursorCoords)
		
		#Draw cursor to screen
		self.screen.blit(self.cursor, self.cursorCoords)

		#Measuring FPS
		self.clock.tick(60) #Tick clock timer
		fps = self.font.render(str(int(self.clock.get_fps())), True, self.pygame.Color('white')) #Get fps
		self.screen.blit(fps, (0, 0)) #Draw FPS on screen

		super().updateUI()


class datasetUI(iTrackerUI):

	def __init__(self):
		super(datasetUI, self).__init__()

		self.dotSize = (100,100)
		self.cursorSize = (100,100)
		self.dot = self.pygame.transform.scale(self.pygame.image.load("UI_assets/pokeball.png"), self.dotSize) 
		self.cursor = self.pygame.transform.scale(self.pygame.image.load("UI_assets/greatball.png"), self.cursorSize) 

		#Load image for dots and cursor and scale to 100x100 pixels
		self.x1 = int(self.wScreenPx*0.5 - self.dotSize[0]/2) 
		self.y1 = int(self.hScreenPx*0.5 - self.dotSize[1]/2)
		self.dotCoords = (self.x1, self.y1)

		#Generating initial coordinates for the cursor
		self.cursorX = int(self.wScreenPx*0.5 - self.cursorSize[0]/2) 
		self.cursorY = int(self.hScreenPx*0.5 - self.cursorSize[1]/2)
		self.cursorCoords = (self.cursorX, self.cursorY) 

	def updateUI(self, prediction, label):
		#calculate difference between prediction & ground truth
		updatedCursorCoords = (label[0]-prediction[0], label[1]-prediction[1])
		#Clears the screen to draw update
		self.screen.fill(self.black)

		#Draw dots on screen
		self.screen.blit(self.dot, self.dotCoords)
		
		#Store updated cursor coordinates
		self.cursorCoords = self.getOffset(updatedCursorCoords)
		
		#Draw cursor to screen
		self.screen.blit(self.cursor, self.cursorCoords)

		#Measuring FPS
		self.clock.tick(60) #Tick clock timer
		fps = self.font.render(str(int(self.clock.get_fps())), True, self.pygame.Color('white')) #Get fps
		self.screen.blit(fps, (0, 0)) #Draw FPS on screen

		super().updateUI()

	def getOffset(self, coords):
		return (round(self.x1 + self.xCm2Px*coords[0]),
				round(self.y1 + -1*self.yCm2Px*coords[1]))

#UI for collecting new gaze training images
#Generates a cursor at random locations on the screen and captures images of the user looking at the cursor
class dataCollectionUI(iTrackerUI):
	def __init__(self, filepath, locationDuration, captureDelay):
		#Initialize cv2
		self.cv2 = __import__('cv2')
		self.random = __import__('random')
		self.datetime = __import__('datetime')
		self.json = __import__('json')

		super(dataCollectionUI, self).__init__()

		#Load image for dots and cursor and scale to 100x100 pixels
		self.filepath = filepath #Directory in which to store the new images

		self.cursorSize = (100,100)
		self.cursor = self.pygame.transform.scale(self.pygame.image.load("UI_assets/pokeball.png"), self.cursorSize)
		self.cursorCoords = self.getRandomCoords()

		#Initialize video capture to collect images from webcam
		self.camera = self.cv2.VideoCapture(0)
		self.imageIndex = 0 #Initialize image index to 0

		#Initialize capture directory
		curDirs = []
		try:
			curDirs = self.os.listdir(filepath)
		except FileNotFoundError:
			self.os.mkdir(self.filepath)

		maxDir = 0
		for directory in curDirs:
			try:
				maxDir = max(maxDir, int(directory))
			except ValueError:
				pass
		self.filepath = filepath + '/' + ('{0:05d}'.format(maxDir + 1))
		self.os.mkdir(self.filepath)		

		#Length of time cursor remains fixed at a given location
		self.locationDuration = locationDuration
		self.elapsedTime = 0
		self.startTime =  self.datetime.datetime.now()
		self.captureDelay = captureDelay

		self.imagesElapsed = 0
		
		self.x = []
		self.y = []
	
	#Capture image from frame
	def captureImage(self):
		retVal, frame = self.camera.read()
		if(retVal):
			self.cv2.imwrite(self.filepath + '/' + ('{0:05d}.jpg'.format(self.imageIndex)), frame)
			self.imageIndex = self.imageIndex + 1
			cmCoords = self.px2Cm(self.cursorCoords)
			self.x.append(cmCoords[0])
			self.y.append(cmCoords[1])

	def px2Cm(self, coords):
		return ((coords[0] + self.cursorSize[0]/2)/self.xCm2Px - self.xCameraOffsetCm,
		-1*((coords[1] + self.cursorSize[1]/2)/self.yCm2Px - self.yCameraOffsetCm))

	def getRandomCoords(self):
		return (self.wScreenPx*self.random.random(), self.hScreenPx*self.random.random()) 

	def updateUI(self):
		print("Updating UI")
		self.elapsedTime = self.datetime.datetime.now() - self.startTime
		
		#Need to generate new cursor location
		if(self.elapsedTime.total_seconds() > self.locationDuration):
			#Generate random cursor coords
			self.cursorCoords = self.getRandomCoords() #Generate random location
			#Time since image location was switched
			self.startTime = self.datetime.datetime.now()
			#Reset elapsed time
			self.elapsedTime = self.startTime - self.startTime
			#Count number of cursor locations that have been finished
			self.imagesElapsed = self.imagesElapsed + 1

		#Clears the screen to draw update
		self.screen.fill(self.black)

		#Draw cursor to screen
		self.screen.blit(self.cursor, self.cursorCoords)
		
		if(self.elapsedTime.total_seconds() > self.captureDelay):
			print("Capturing Image: " + str(self.imagesElapsed))
			self.captureImage()

		super().updateUI()
		return self.imagesElapsed

	def writeData(self):
		with open(self.filepath + '/' + 'dotinfo.json', 'w') as fp:
			self.json.dump(
				{
					'XCam' : self.x,
					'YCam' : self.y
				},
				fp
			)


	






# ui = datasetUI();
# while 1:
# 	for x,y in zip(range(1000, 3000), range(1000, 3000)):
# 		ui.updateUI((-1, -1))