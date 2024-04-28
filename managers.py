from pygame_widgets.slider import Slider
from pygame_widgets.toggle import Toggle
import pygame
import math
import random
import csv
from vehicles import Obstacle, Car
from visualise import *

# Defining constants
CONST_TOPSPEED = 180
CONST_T = 1.5
CONST_A_MAX = 4.38
DEF_NUM_OF_CARS = 30
CONST_DT = 1/(FPS)
CONST_CIRCLE_CENTRE = (SCREEN_WIDTH/2 + 240,SCREEN_HEIGHT/2)
BLACK = (0, 0, 0)
DEFAULT_NOISE = True
DEFUALT_NUM_AV = 0
FINAL_TIME = 600

# This class is responsible for calculating Traffic Flow
class LapCounter:
    def __init__(self):
        self.totalLaps = 0
        self.trafficFlow = 0
        self.interval = 0
        self.laps = 0
        self.lapList = []
        self.simTime = 0
   
   # Register new laps in the list of laps
    def addLaps(self, cars):
        for car in cars:
            if car.lapCheck():
                self.laps = 1                

        self.lapList.append([self.laps, self.simTime])
        self.laps = 0

    # Calculate how many laps are in the list, 
    # trim the list to the data from with the last minute
    def countTotalLaps(self):
        laps = []
        for i in self.lapList:
            if((self.simTime - i[1]) > 60):
                self.lapList.pop(0)
            else:
                laps.append(i[0])
        self.totalLaps = sum(laps)

    # Calculate Traffic flow and return as a string
    def calTrafficFlow(self, cars, simTime):
        self.simTime = simTime
        self.addLaps(cars)
        self.countTotalLaps()

        if simTime >= 60:
            return str(self.totalLaps)  # if simTime > 60 -> return Traffic flow [cars/min]
        else:
            return 'Calculating... [wait '+str(round((60 - simTime),1)) +'s]'

# This class is responsible for managing the operation of sliders in the GUI
class SliderManager:
    def __init__(self):
        # Initialise sliders
        self.slider = Slider(SCREEN, 40, 200, 400, 10, min=2, max=30, step=1)
        self.slider1 = Slider(SCREEN, 40, 280, 400, 10, min=1, max=240, step=1)
        self.slider2 = Slider(SCREEN, 40, 360, 400, 10, min=0, max=10, step=0.5)
        self.slider3 = Slider(SCREEN, 40, 440, 400, 10, min=0.2, max=10, step=0.01)
        self.slider4 = Slider(SCREEN, 40, 520, 400, 10, min=1, max=10, step=1)
        self.slider5 = Slider(SCREEN, 270, 600, 170, 10, min=0, max=DEF_NUM_OF_CARS, step=1)

        self.slider.setValue(DEF_NUM_OF_CARS)
        self.slider1.setValue(CONST_TOPSPEED)
        self.slider2.setValue(CONST_T)
        self.slider3.setValue(CONST_A_MAX)
        self.slider4.setValue(10)
        self.slider5.setValue(DEFUALT_NUM_AV)

        self.prevValue = self.slider.getValue()
        self.prevValue1 = self.slider1.getValue()
        self.prevValue2 = self.slider2.getValue()
        self.prevValue3 = self.slider3.getValue()
        self.prevValue4 = self.slider4.getValue()
        self.prevValue5 = 0

        self.resetSimTime = False   # A variable used for reseting the simulation

    # Restart the sliders values to default
    def resetSliders(self):
        self.slider.setValue(DEF_NUM_OF_CARS)
        self.slider1.setValue(CONST_TOPSPEED)
        self.slider2.setValue(CONST_T)
        self.slider3.setValue(CONST_A_MAX)
        self.slider4.setValue(10)
        self.slider5.setValue(DEFUALT_NUM_AV)

    # Update sliders
    def updateSliders(self, cars):
        # Number of vehicles slider
        self.newValue = self.slider.getValue()
        if self.prevValue != self.newValue:

            # Update the list of cars with the new vehicles
            # evenly space cars on the circle
            cars = []
            angDist = math.radians(360/self.newValue)
            for i in range(self.newValue):
                cars.append(Car(i*angDist, cars,angDist))

            # Set the values of other sliders to default values
            self.slider1.setValue(CONST_TOPSPEED)
            self.slider2.setValue(CONST_T)
            self.slider3.setValue(CONST_A_MAX)
            self.slider4.setValue(10)

            # Reinitialise AV slider
            self.slider5.disable()
            self.slider5.hide()
            self.slider5 = Slider(SCREEN, 270, 600, 170, 10, min=0, max=self.newValue, step=1)
            self.slider5.setValue(0)
            self.resetSimTime = True    # Reset simulation time if num of vehicles changed
            self.prevValue = self.newValue

        # Max speed slider
        self.newValue1 = self.slider1.getValue()
        if self.prevValue1 != self.newValue1:
            for car in cars:
                car.setMaxSpeed(round(self.newValue1, 2))
            self.prevValue1 = self.newValue1

        # Time gap slider
        self.newValue2 = self.slider2.getValue()
        if self.prevValue2 != self.newValue2:
            for car in cars:
                car.setTimeGap(round(self.newValue2, 2))
            self.prevValue2 = self.slider2.getValue()

        # Max acceleration slider
        self.newValue3 = self.slider3.getValue()
        if self.prevValue3 != self.newValue3:
            for car in cars:
                car.setMaxAcc(round(self.newValue3, 2))
            self.prevValue3 = self.newValue3

        # Time multiplier slider
        self.newValue4 = self.slider4.getValue()
        self.prevValue4 = self.newValue4

        # Autonomous vehicles sliders
        self.newValue5 = self.slider5.getValue()
        if self.prevValue5 != self.newValue5:
            for car in cars:
                car.setDefault()
            i = 0
            random.shuffle(cars)
            for car in cars:
                if i >= self.newValue5:
                    break
                car.setAutonomous()
                i += 1
            self.prevValue5 = self.newValue5

            # sort cars
            cars.sort(key=lambda car: car.angle, reverse=False) 
            cars = sorted(cars, key=lambda car: car.angle, reverse=False)

        return cars
    
    # Return the value of resetSimTime variable
    def getResetSimTime(self):
        return self.resetSimTime
    
    # Return the number of AV vehicles
    def getACNum(self):
        return self.newValue5
    
    # Return the timelapse value
    def getTimeStep(self):
        return self.newValue4

# This class mangages the operation of toggle switches in the GUI
class ToggleManager:
    def __init__(self):
        # Initialise the toggle switch
        if DEFAULT_NOISE:
            self.toggle = Toggle(SCREEN, 40, 595, 60, 15,startOn=True)
            self.prevState = False  # Leaving this False to ensure settings are applied
        else:
            self.toggle = Toggle(SCREEN, 40, 595, 60, 15)
            self.prevState = False

    # Check the switch state and update relevant variables
    def toggleCheck(self, cars):
        if (self.toggle.getValue() & (self.toggle.getValue() != self.prevState)):
            for car in cars:
                car.setNoise()      # Switch triggered -> add noise to model parameters
        elif ((not self.toggle.getValue()) & (self.toggle.getValue() != self.prevState)):
            for car in cars:
                car.removeNoise()   # Switch disabled -> remove noise to model parameters

        self.prevState = self.toggle.getValue()

    # Reset the switch state to default
    def toggleReset(self):
        if (DEFAULT_NOISE != self.toggle.getValue()):
            self.toggle.toggle()

# This class manages the buttons in the GUI
class buttonManager:
    def __init__(self):
        # Initialise buttons
        self.button_quit = pygame.Rect(20,640,210,60)
        self.button_reset = pygame.Rect(250,640,210,60)
        self.button_obstacle = pygame.Rect(800,520,160,40)

# This class manages the simulation data saved as a CSV
class dataManager:

    # Initialise / Clear the data file
    def initFile():
        # Using csv.writer method from CSV package
        with open('speed.csv', 'w', newline='') as f:
            write = csv.writer(f)
        with open('acc.csv', 'w', newline='') as f:
            write = csv.writer(f)
        with open('pos.csv', 'w', newline='') as f:
            write = csv.writer(f)
        with open('avs.csv', 'w', newline='') as f:
            write = csv.writer(f)
        
    # Append more data to the file
    def appendData(data, filename):
        with open(filename, 'a', newline='') as f:
            # using csv.writer method from CSV package
            write = csv.writer(f)
            for row in data:
                write.writerow(row)
            f.close()

# The simulation manager class which is the main class of the whole program
class simManager:

    # Initialise simulation variables
    def __init__(self):
        self.run = True
        self.cars = []
        self.cars_unsorted = []
        angDist = math.radians(360/DEF_NUM_OF_CARS)
        for i in range(DEF_NUM_OF_CARS):
            self.cars.append(Car(i*angDist, self.cars, angDist))
        self.roadObjects = []
        self.plotData = []
        self.obstacles = []
        self.simTime = 0
        self.data_speed = []
        self.data_acc = []
        self.data_pos = []
        self.lapCounter = LapCounter()
        self.sm = SliderManager()
        self.tm = ToggleManager()
        self.bm = buttonManager()
        self.events = pygame.event.get()
        self.valTrafficFlow = ""
        self.first_id = 0
        self.deltaT = 30
        #dataManager.initFile()

    # Run the simulation
    def simRun(self):
        self.updateEvents()         # Check for keyboard inputs
        self.updateCarParams()      # Check for changes in noise toggle
        self.updateRoadObjects()    # Check for changes in slider values

        # If new vehicles were added, reset the simulation
        if self.sm.getResetSimTime():   
            self.resetSimulation()

        for i in range(self.sm.getTimeStep()):
            self.sortRoadObejcts()      # Sort the list of Road Objects
            self.updateCarPositions()   # Calculate car positions using IDM
            self.updateSimTime()        # Update Simulation Time by delta_t
        
        # Calcuate Traffic Flow
        self.valTrafficFlow = self.lapCounter.calTrafficFlow(self.cars, self.simTime)
        
        self.storeData()            # Store the Position, Speed and Acceleration data
        self.drawSimulation()       # Draw the simulation results to the window

        # TO SAVE THE DATA, UNCOMMENT THE SECTION BELOW
        """
        # Simulation time
        if self.simTime >= FINAL_TIME:
            self.run = False
            self.saveData()
        """

    # Check for user inputs
    def updateEvents(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.bm.button_quit.collidepoint(event.pos):
                    self.run = False
                if self.bm.button_reset.collidepoint(event.pos):
                    self.resetSimulation()
                    self.sm.resetSliders()
                # Adding / Removing of the obstacle
                if self.bm.button_obstacle.collidepoint(event.pos):
                    if self.obstacles:
                        self.obstacles = []
                    else:
                        self.obstacles.append(Obstacle(math.pi/2, self.cars))
                        print("An obstacle introduced at: " + "%.2f" % self.simTime + "s")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.slowDownFirst()
                if event.key == pygame.K_UP:
                    self.restartFirst()
    
    # Update the list of road objects (check for new cars / obstacles)
    def updateRoadObjects(self):
        self.roadObjects = []
        self.roadObjects = self.sm.updateSliders(self.cars)
        if self.obstacles:
            for ob in self.obstacles:
                self.roadObjects.append(ob)
    
    # Resets the simulation time and switches, removes the obstacles and reinitialises data files
    def resetSimulation(self):
        self.simTime = 0
        self.sm.resetSimTime = False
        self.obstacles = []
        self.tm.toggleReset()
        #dataManager.initFile()

    # Sorts the road objects list to determine their order (required for distance recognition)
    def sortRoadObejcts(self):
        self.roadObjects.sort(key=lambda ro: ro.angle, reverse=False) 
        self.roadObjects = sorted(self.roadObjects, key=lambda ro: ro.angle, reverse=False)

    # Updates cars position & the list of cars
    def updateCarPositions(self):
        self.cars = []
        roadObjects_tmp = self.roadObjects
        for ro in self.roadObjects:
            if ro.isCar:
                ro.updatePosition(roadObjects_tmp)
                self.cars.append(ro)
            
    # Update car parameters
    def updateCarParams(self):
        self.tm.toggleCheck(self.cars)  # Check if switch state changed

    # Update simulation time
    def updateSimTime(self):
        self.simTime = self.simTime + self.cars[0].dt

    # Draw the simulation
    def drawSimulation(self):
        # Creating a list of strings used as labels in the GUI
        labels = [self.valTrafficFlow, str(len(self.cars)), str(round(self.sm.slider1.getValue()/6,2)), str(self.sm.slider2.getValue()), str(round(self.sm.slider3.getValue()/6,2)), str(self.sm.slider4.getValue()), str(round(self.simTime,2)), str(self.sm.getACNum())]
        Draw.drawSimulation(Draw, self.cars, labels, self.bm, self.events, self.obstacles)

    # Preparing data for saving in the file
    def storeData(self):
        self.cars_unsorted.sort(key=lambda c: c.id, reverse=False) 
        self.cars_unsorted = sorted(self.cars, key=lambda c: c.id, reverse=False)
        
        speed_row = [self.simTime]
        acc_row = [self.simTime]
        pos_row = [self.simTime]

        for car in self.cars_unsorted:
            speed_row.append(car.speed/6)   # Converting speed to m/s
            acc_row.append(car.a/6)         # Converting acceleration to m/s^2
            pos_row.append(car.x/6)         # Converting position to m
        
        self.data_speed.append(speed_row)   # Converting speed to m/s
        self.data_acc.append(acc_row)       # Converting acceleration to m/s^2
        self.data_pos.append(pos_row)       # Converting position to m

    def saveData(self):
        dataManager.appendData(self.data_speed,'speed.csv')
        dataManager.appendData(self.data_acc,'acc.csv')
        dataManager.appendData(self.data_pos,'pos.csv')
        dataManager.appendData(self.listAVs(),'avs.csv')

    # Return the run variable
    def getRun(self):
        return self.run
    
    # Slow down the leading vehicle
    def slowDownFirst(self):
        i = 0
        for car in self.roadObjects:
            if car.isCar:
                if car.getID() == (len(self.cars) - 1):
                    self.roadObjects[i].topspeed = (self.roadObjects[i].core_topspeed/20)
                    self.first_id = (len(self.cars) - 1)
            i += 1

    # Reset the leading vehicle speed to default
    def restartFirst(self):
        for ro in self.roadObjects:
            if ro.isCar:
                if ro.getID() == self.first_id:
                    ro.setMaxSpeed(ro.core_topspeed)
                    break

    # Create a list of IDs of AVs -> Used for plotting the data
    def listAVs(self):
        self.cars_unsorted.sort(key=lambda c: c.id, reverse=False) 
        self.cars_unsorted = sorted(self.cars, key=lambda c: c.id, reverse=False)
        
        avList = []
        for car in self.cars_unsorted:
            if car.autonomous:
                avList.append([car.id])
        return avList
    

