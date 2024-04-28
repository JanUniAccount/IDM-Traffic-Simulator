import random
import pygame
import math
import numpy

# Defining constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
                        # Real values
CONST_TOPSPEED = 180    # 30 m/s
CONST_T = 1.5           # 1.5 s
CONST_A_MAX = 4.38      # 0.73 m/s^2
CONST_B_MAX = 10.02     # 1.67 m/s^2
CONST_DT = 1/(FPS)
CONST_CIRCLE_CENTRE = (SCREEN_WIDTH/2 + 240,SCREEN_HEIGHT/2)
BLACK = (0, 0, 0)

# Parent class storing information about all objects on the road
class RoadObject:
    def __init__(self, a):
        self.angle = a
        self.l = 20
        self.speed = 0
        self.roadRadius = 300
        self.isCar = False
        self.positionX = CONST_CIRCLE_CENTRE[0] + math.cos(self.angle) * self.roadRadius
        self.positionY = CONST_CIRCLE_CENTRE[1] + math.sin(self.angle) * self.roadRadius

# Child class of Road Object, managing and storing information about cars
class Car(RoadObject):

    # Intitialise using position and a list of cars (used for indexing)
    def __init__(self, pos, cars, gap):
        super().__init__(pos)
        self.id = 0             # Unique id of a car
        self.dt = CONST_DT      # Simulation step time
        self.isCar = True       # Car road object
        self.autonomous = False # Autonomous -> False by default

        self.noise = 0  # Initial noise
        self.a = 0      # Initial acceleration
        self.speed = 0  # initial velocity
       
        # Defining key parameters
        self.a_max = CONST_A_MAX  # Max acceleration
        self.b_max = CONST_B_MAX  # Max decceleration
        self.T = CONST_T          # Desired time headway
        self.topspeed = CONST_TOPSPEED  # Desired velocity
        self.l = 30               # Car length

        # Defining core parameters (noise-resistant)
        self.core_a_max = CONST_A_MAX
        self.core_b_max = CONST_B_MAX
        self.core_T = CONST_T
        self.core_topspeed = CONST_TOPSPEED

        self.s0 = 15            # Min desired distance
        
        self.x = pos*self.roadRadius    # Position on the circle
        self.initX = self.x
        self.initGap = gap
        self.angle = pos                # Position on the circle (angle)
        self.prevAngle = pos            # Previous position on the circle (angle)
        self.sqrt_ab = 0                # IDM parameter

        # Visual parameters setup
        self.visible = True
        self.rotatedImage = None
        self.image = None
        self.image_orig = None
        self.rect = None

        # Loading car textures
        self.img_car = pygame.image.load('images/car.png')
        self.img_car_breaking = pygame.image.load('images/car_breaking.png')
        self.img_ac = pygame.image.load('images/ac.png')
        self.img_ac_breaking = pygame.image.load('images/ac_breaking.png')

        # Running setup functions
        self.initParameters(cars)
        self.visualSetup()
        self.updateRotation()
        self.updateTarget()

    # Calculate initial parameters of a car
    def initParameters(self, cars):
        self.sqrt_ab = 2*numpy.sqrt(self.a_max*self.b_max)
        self.positionX = CONST_CIRCLE_CENTRE[0] + math.cos(self.angle) * self.roadRadius
        self.positionY = CONST_CIRCLE_CENTRE[1] + math.sin(self.angle) * self.roadRadius
        self.ID = self.genUID(cars)

    # Load and setup car textures
    def visualSetup(self):
        self.image_orig = self.img_car  
        self.image = self.image_orig.copy() # Creating a copy of orignal image for smooth rotation  
        self.rect = self.image.get_rect()   # Define rect for placing the rectangle at the desired position  
        self.rect.center = (self.positionX, self.positionY) 

    # Rotating the car based on its position on the circle
    def updateRotation(self):
        self.rotatedImage = pygame.transform.rotate(self.image_orig , math.degrees(math.pi/2 - self.angle))

    # Update car position and kinematics
    def updatePosition(self, cars):
        if len(cars) > 1:
            i = 0
            
            # Determine the position of self in the list of cars
            for car in cars:
                if(car.x == self.x):
                    break
                else:
                    i += 1

            if(i < (len(cars) - 1)):       
                car = cars[i+1]
            elif(i == (len(cars) - 1)):     # Self is the last car on the list
                car = cars[0]

            if(self.getID() < len(cars)-1):
                gap = car.x - self.x
            else: 
                road_length = 2*math.pi*self.roadRadius
                gap = car.x - (self.x - (road_length))
            
            delta_x = gap - car.l               # Distance to the next car
            delta_v = self.speed - car.speed    # Difference of speed between self and the next car

            self.euler_step(delta_x, delta_v)

            if self.speed + self.a*self.dt < 0:
                # Negative speed fix
                self.x -= 1/2*self.speed*self.speed/self.a
                self.speed = 0

        self.updateVisuals()
        self.updateTarget()   

    # Updating car visuals
    def updateVisuals(self):
        
        # Visualising if the vehicle is accelerating or stopping with consideration of car type
        if not self.autonomous:
            if self.a < 0:
                self.image_orig = self.img_car_breaking 
            else:
                self.image_orig = self.img_car 
        else:
            if self.a < 0:
                self.image_orig = self.img_ac_breaking  
            else:
                self.image_orig = self.img_ac

        self.updateRotation()
        self.rect.center = (self.positionX, self.positionY) # Update coordinates of the car
        old_center = self.rect.center   # Making a copy of the old center of the rectangle  
        self.rect = self.rotatedImage.get_rect()  
        self.rect.center = old_center   # Set the rotated rectangle to the old center 

    # Calculating the next position of the car on the circle
    def updateTarget(self):

        # Angular position of car on the circle
        self.angle = self.x/self.roadRadius
        
        # Translate angular position to range from 0 to 2pi
        if self.angle > 2*math.pi:
            val = 0
            for i in range(math.floor(self.angle/(2*math.pi))):
                val = i
            self.angle -= (val+1)*(2*math.pi)

        # Update position of the car on the circle
        self.positionX = CONST_CIRCLE_CENTRE[0] + math.cos(self.angle) * self.roadRadius
        self.positionY = CONST_CIRCLE_CENTRE[1] + math.sin(self.angle) * self.roadRadius

    def setMaxSpeed(self, val):
        self.topspeed = val
        self.core_topspeed = val

    def setTimeGap(self, val):
        self.T = val
        self.core_T = val

    def setMaxAcc(self, val):
        self.a_max = val - self.noise
        self.core_a_max = val

    def setDt(self,val):
        self.dt = val

    # After each lap, newLap becomes true
    def lapCheck(self):
        if (self.angle + 0.1) < self.prevAngle:
            newLap = True
        else:
            newLap = False
        
        self.prevAngle = self.angle
        
        return newLap

    def setNoise(self):
        self.noise = random.random()            # Noise value ranges from 0 to 1
        self.a_max = self.a_max - self.noise    # Max acceleration with noise

    # Removes noise and restores the default parameter values
    def removeNoise(self):
        self.noise = 0
        self.a_max = self.core_a_max
        self.b_max = self.core_b_max
        self.T = self.core_T
        self.topspeed = self.core_topspeed

    # Sets car into autonomous mode
    def setAutonomous(self):
        self.a_max = 22.8
        self.T = 0.6
        self.topspeed = 12
        self.autonomous = True

    # Removes noise and restores the default parameter values, autonomous parameter is disabled as well
    def setDefault(self):
        self.noise = 0
        self.a_max = self.core_a_max
        self.b_max = self.core_b_max
        self.T = self.core_T
        self.topspeed = self.core_topspeed
        self.autonomous = False

    # Generate unique car id
    def genUID(self,cars):
        id = 0
        for car in cars:
            id += 1
        self.id = id
    
    def getID(self):
        return self.id
    
    # Perform one step of RK4 integration for IDM model
    def rk4_step(self, delta_x, delta_v):
        dt = self.dt
        v = self.speed
        x = self.x

        k1v = self.idmStep(v, delta_v, delta_x)
        k1x = v
        
        k2v = self.idmStep(v + 0.5 * k1v * dt, delta_v, delta_x)
        k2x = v + 0.5 * k1x * dt
        
        k3v = self.idmStep(v + 0.5 * k2v * dt, delta_v, delta_x)
        k3x = v + 0.5 * k2x * dt
        
        k4v = self.idmStep(v + k3v * dt, delta_v, delta_x)
        k4x = v + k3x * dt
        
        self.speed = v + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        self.x = x + (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
    
    # Perform one step of Euler integration for IDM model.
    def euler_step(self, delta_x, delta_v):
        v = self.speed
        x = self.x

        self.speed += self.idmStep(v,delta_v,delta_x)*self.dt
        self.x += self.speed*self.dt

    # IDM Implementation
    def idmStep(self, v, delta_v, delta_x):

        # Calculating alpha value -> used in acceleration calculations
        alpha = (self.s0 +  max(0, self.T*v + delta_v*v/self.sqrt_ab)) / delta_x

        # Update acceleration based on max acceleration and alpha
        a = self.a_max * (1-(v/self.topspeed)**4 - alpha**2)
        
        # Limiting decceleration
        if a < -self.b_max:
            a = -28.2

        self.a = a

        return a


# Obstacle class
class Obstacle(RoadObject):
    def __init__(self, pos, cars):
        super().__init__(pos)
        self.initCars = cars
        self.x = self.setPosition()   # Position on the circle
        self.updatePosition()

    # Set the position of the traffic cone in front of the leading vehicle
    def setPosition(self):
        prevVal = 0
        for car in self.initCars:
            if car.x > prevVal:
                leadingCar = car
                prevVal = car.x
        offset = 60
        self.angle = leadingCar.angle + offset/(self.roadRadius)
        return leadingCar.x + offset
    
    def updatePosition(self):
        self.positionX = CONST_CIRCLE_CENTRE[0] + math.cos(self.angle) * self.roadRadius
        self.positionY = CONST_CIRCLE_CENTRE[1] + math.sin(self.angle) * self.roadRadius
