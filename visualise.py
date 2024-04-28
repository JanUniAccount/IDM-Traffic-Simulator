import pygame
import pygame_widgets

# Defining constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
GREEN = (0, 255, 0)
ORANGE = (220, 100, 0)

CONST_CIRCLE_CENTRE = (SCREEN_WIDTH/2 + 240,SCREEN_HEIGHT/2)

# Define simulation window
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('IDM Traffic Simulator')     # Set window title 

# Define fonts
fontTitle = pygame.font.Font('fonts/Roboto-Bold.ttf', 47)
fontSubTitle = pygame.font.Font('fonts/Roboto-Medium.ttf', 24)
font = pygame.font.Font('fonts/Roboto-Regular.ttf',24)
img_cone = pygame.image.load('images/cone.png')

# Load car textures
img_car = pygame.image.load('images/car.png')
img_car_breaking = pygame.image.load('images/car_breaking.png')
img_ac = pygame.image.load('images/ac.png')
img_ac_breaking = pygame.image.load('images/ac_breaking.png')

# Draw class is responsible for visualising of the simulation
class Draw: 

     # The main draw function, draws the whole simulation
    def drawSimulation(self, cars, texts, bm, events, obstacles):
        SCREEN.fill(WHITE)
        self.drawGrid()
        self.drawMenu(self, texts, bm)
        self.drawSliders(events)
        self.drawCircle()
        self.drawCars(cars)
        self.drawObstacle(obstacles)
        pygame.display.flip()
        pygame.display.update()

    # Draw the grid       
    def drawGrid():
        blockSize = 40 # Set the size of the grid block
        for x in range(0, SCREEN_WIDTH, blockSize):
            for y in range(0, SCREEN_HEIGHT, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(SCREEN, GRAY, rect, 1)

    # Draw cars
    def drawCars(cars):
        for car in cars:
            if car.visible:
                SCREEN.blit(car.rotatedImage , car.rect)

    # Draw obstacles
    def drawObstacle(obstacles):
        if not obstacles:
            pass
        else:
            for obstacle in obstacles:
                SCREEN.blit(img_cone, (obstacle.positionX-10, obstacle.positionY-10))

    # Draw the roundabout
    def drawCircle():
        pygame.draw.circle(SCREEN, (51, 102, 204), CONST_CIRCLE_CENTRE, 320, width=40)
        pygame.draw.circle(SCREEN, (50, 50, 50), CONST_CIRCLE_CENTRE, 324, width=5)
        pygame.draw.circle(SCREEN, (50, 50, 50), CONST_CIRCLE_CENTRE, 284, width=5)

    # Draw the user interface and texts
    def drawMenu(self, texts, bm):

        # Drawing main menu panels
        pygame.draw.rect(SCREEN, WHITE, pygame.Rect(0, 0, 480, 720))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(0, 0, 480, 52))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 80, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 160, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 240, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 320, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 400, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 480, 440, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(20, 560, 210, 60))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(250, 560, 210, 60))
        pygame.draw.rect(SCREEN, WHITE, pygame.Rect(1080, 680, 200, 40))
        pygame.draw.rect(SCREEN, WHITE, pygame.Rect(720, 240, 320, 200))
        pygame.draw.rect(SCREEN, GRAY, pygame.Rect(720, 240, 320, 40))

        # Title
        title = Text((0, 0),'IDM Traffic Simulator')
        title.text = fontTitle.render(' IDM Traffic Simulator ', True, BLACK)
        self.drawText(title)

        # Traffic Flow
        text = Text((30, 80),'Traffic Flow Q [cars/min]:')
        text.text = fontSubTitle.render('Traffic Flow Q [cars/min]:', True, BLACK)
        self.drawText(text)

        text = Text((30, 110),'')
        text.text = font.render(texts[0], True, BLACK)
        self.drawText(text)

        # Number of cars
        text = Text((30, 160),'')
        text.text = fontSubTitle.render('Number of cars: '+ texts[1], True, BLACK)
        self.drawText(text)

        # Max speed
        text = Text((30, 240),'')
        text.text = fontSubTitle.render('Maximum speed [m/s]: '+ texts[2], True, BLACK)
        self.drawText(text)

        # Time gap
        text = Text((30, 320),'')
        text.text = fontSubTitle.render('Time gap [s]: '+ texts[3], True, BLACK)
        self.drawText(text)

        # Max acceleration
        text = Text((30, 400),'')
        text.text = fontSubTitle.render('Maximum acceleration [m/s^2]: ' + texts[4], True, BLACK)
        self.drawText(text)

        # Time multiplier
        text = Text((30, 480),'')
        text.text = fontSubTitle.render('Time multiplier: ' + texts[5], True, BLACK)
        self.drawText(text)

        # Parameter noise
        text = Text((30, 560),'')
        text.text = fontSubTitle.render('Parameter noise', True, BLACK)
        self.drawText(text)

        # Simulation time
        text = Text((1090, 685),'')
        text.text = fontSubTitle.render('Time [s]: ' + texts[6], True, BLACK)
        self.drawText(text)

        # Number of AVs
        text = Text((260, 560),'')
        text.text = fontSubTitle.render('AV: ' + texts[7] + ' out of ' + texts[1], True, BLACK)
        self.drawText(text)

        # Title: legend
        text = Text((730, 245),'')
        text.text = fontSubTitle.render('Legend', True, BLACK)
        self.drawText(text)

        # Buttons
        surf = fontSubTitle.render('Quit', True, 'white')
        a,b = pygame.mouse.get_pos()
        if bm.button_quit.x <= a <= bm.button_quit.x + 210 and bm.button_quit.y <= b <= bm.button_quit.y +60:
            pygame.draw.rect(SCREEN,(180,180,180),bm.button_quit)
        else:
            pygame.draw.rect(SCREEN, (110,110,110),bm.button_quit)

        SCREEN.blit(surf,(bm.button_quit.x + 80, bm.button_quit.y+10))

        surf = fontSubTitle.render('Reset', True, 'white')
        a,b = pygame.mouse.get_pos()
        if bm.button_reset.x <= a <= bm.button_reset.x + 210 and bm.button_reset.y <= b <= bm.button_reset.y +60:
            pygame.draw.rect(SCREEN,(180,180,180),bm.button_reset)
        else:
            pygame.draw.rect(SCREEN, (110,110,110),bm.button_reset)

        SCREEN.blit(surf,(bm.button_reset.x + 80, bm.button_reset.y+10))

        surf = fontSubTitle.render('Place', True, 'white')
        a,b = pygame.mouse.get_pos()
        if bm.button_obstacle.x <= a <= bm.button_obstacle.x + 160 and bm.button_obstacle.y <= b <= bm.button_obstacle.y + 40:
            pygame.draw.rect(SCREEN,(180,180,180),bm.button_obstacle)
        else:
            pygame.draw.rect(SCREEN, (110,110,110),bm.button_obstacle)

        SCREEN.blit(surf,(bm.button_obstacle.x+40, bm.button_obstacle.y+5))
        SCREEN.blit(img_cone,(bm.button_obstacle.x+110, bm.button_obstacle.y+10))
        
        # -----------------------------------
        # Legend
        # -----------------------------------

        # Images
        SCREEN.blit(img_car, (735, 300))
        SCREEN.blit(img_car_breaking, (775, 300))
        SCREEN.blit(img_ac, (735, 350))
        SCREEN.blit(img_ac_breaking, (775, 350))
        SCREEN.blit(img_cone, (785, 400))

        # Titles
        text = Text((815, 295),'')
        text.text = font.render('Default car', True, BLACK)
        self.drawText(text)

        text = Text((815, 345),'')
        text.text = font.render('Autonomous car', True, BLACK)
        self.drawText(text)

        text = Text((815, 395),'')
        text.text = font.render('Road obstacle', True, BLACK)
        self.drawText(text)

    # Draw and update sliders
    def drawSliders(events):
        pygame_widgets.update(events)

    # Support function for visualising Text objects
    def drawText(text):
        SCREEN.blit(text.text, text.textRect)  

# Text class
class Text:
    def __init__(self, pos, txt):
        # Create a font object
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        
        # Create a text surface object, on which text is drawn
        self.text = self.font.render(txt, True, BLACK, GRAY)
        
        # Create a rectangular object for the text surface object
        self.textRect = self.text.get_rect()
        
        self.textRect.topleft = pos # Set the center of the rectangular object