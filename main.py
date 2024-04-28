"""
IDM Traffic Simulator.
Made by: Jan Slusarski
Final Year Project Title: Reproducing and eliminating udesirable 
traffic phenomena using the IDM and traffic control strategies.
Date: April 2024
"""

import pygame # Activate the pygame library
pygame.init()   # Initiate pygame

from managers import simManager
from managers import FPS
from visualise import *

clock: pygame.time.Clock = pygame.time.Clock()  # Initialise the simulation clock

# Main function definition
def main():
    sm = simManager()   # Create simulation manager instance
    
    # Simulation while loop
    while sm.getRun():
        clock.tick(FPS)     # Update the clock
        sm.simRun()         # Run the simulation

    pygame.quit()   # Quit pygame
    
main()