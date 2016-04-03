import pygame
import ConfigParser
import os

configfilename = os.path.join("saves","controls.cfg")
config = ConfigParser.ConfigParser()
config.read(configfilename)

pygame.display.init()
pygame.font.init()

window = pygame.display.set_mode()

