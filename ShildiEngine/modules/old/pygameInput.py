import pygame, sys, random
import pygame.locals as pgl

class pygame_landschaft():
    def __init__(self,datafile,landschaftsname=None,title="pygame",width=400,height=400):
        # set up pygame
        pygame.init()
        self.mainClock = pygame.time.Clock()
        
        # set up the window
        self.WINDOWWIDTH = width
        self.WINDOWHEIGHT = height
        self.windowSurface = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT)
                                               #,pygame.FULLSCREEN
                                               )
        self.title=title
        pygame.display.set_caption(self.title)

class ding():
    def __init__(self,datafile):
        self.datafile = datafile

verzeichnis = "/home/joram/Shildiwelt/data/Objekte/Landschaftssegmente/"
landi = pygame_landschaft(verzeichnis)

player = pygame.Rect(300, 100, 50, 50)
foods = []
FOODSIZE = 10
for i in range(20):
    foods.append(pygame.Rect(random.randint(0, landi.WINDOWWIDTH - FOODSIZE),
                             random.randint(0, landi.WINDOWHEIGHT - FOODSIZE),
                             FOODSIZE, FOODSIZE))

# set up movement variables
moveLeft = False
moveRight = False
moveUp = False
moveDown = False

MOVESPEED = 6

# ...................................  Modul .....................................

_keydown_bindings = {}
_keyup_bindings = {}

def onkey(func, key):
    """Bind an action to a key press event"""
    if type(key) == str and len(key) == 1:
        key = ord(key)
    _keydown_bindings[key] = func
        

def onkeyrelease(func, key):
    """Bind an action to a key release event"""
    if type(key) == str and len(key) == 1:
        key = ord(key)
    _keyup_bindings[key] = func
    
    
class Ding(object):
    pass

# ...................................   Test ..........................

def setmove(wohin,what):
    global moveRight, moveLeft, moveUp, moveDown
    if wohin == 'left':
        moveLeft = what
    elif wohin == "right":
        moveRight = what
    elif wohin == "up":
        moveUp = what
    elif wohin == "down":
        moveDown = what

def beenden():
    pygame.quit()
    sys.exit()

def randomove():
    player.top = random.randint(0, landi.WINDOWHEIGHT - player.height)
    player.left = random.randint(0, landi.WINDOWWIDTH - player.width)

for direction in [("left",pgl.K_LEFT),("right",pgl.K_RIGHT),
                  ("up",pgl.K_UP),("down",pgl.K_DOWN),]:
    onkey(lambda wohin=direction[0]: setmove(wohin,True), direction[1])
    onkeyrelease(lambda wohin=direction[0]: setmove(wohin,False), direction[1])


onkey(beenden,pgl.K_ESCAPE)
onkey(randomove,"x")

foodCounter=0
NEWFOOD=5

# run the game loop
while True:
    # check for events
    for event in pygame.event.get():
        if event.type == pgl.QUIT:
            beenden()
        if event.type == pgl.KEYDOWN:
            try:
                _keydown_bindings[event.key]()
            except KeyError: # Achtung Keyerror in der eingebundenen Funktion werden nicht gesondert behandelt!
                pass

        if event.type == pgl.KEYUP:
            try:
                _keyup_bindings[event.key]()
            except KeyError: # Achtung Keyerror in der eingebundenen Funktion werden nicht gesondert behandelt!
                pass
            
        if event.type == pgl.MOUSEBUTTONUP:
            foods.append(pygame.Rect(event.pos[0], event.pos[1], FOODSIZE, FOODSIZE))

    foodCounter += 1
    if foodCounter >= NEWFOOD:
        # add new food
        foodCounter = 0
        foods.append(pygame.Rect(random.randint(0, landi.WINDOWWIDTH - FOODSIZE), random.randint(0, landi.WINDOWHEIGHT - FOODSIZE), FOODSIZE, FOODSIZE))

    # draw the (255,255,255) background onto the surface
    landi.windowSurface.fill((0,0,0))

    # move the player
    if moveDown and player.bottom < landi.WINDOWHEIGHT:
        player.top += MOVESPEED
    if moveUp and player.top > 0:
        player.top -= MOVESPEED
    if moveLeft and player.left > 0:
        player.left -= MOVESPEED
    if moveRight and player.right < landi.WINDOWWIDTH:
        player.left += MOVESPEED

    # draw the player onto the surface
    pygame.draw.rect(landi.windowSurface, (255,255,255), player)

    # check if the player has intersected with any food squares.
    for food in foods[:]:
        if player.colliderect(food):
            foods.remove(food)

    # draw the food
    for i in range(len(foods)):
        pygame.draw.rect(landi.windowSurface, (0,255,0), foods[i])

    # draw the window onto the screen
    pygame.display.update()
    landi.mainClock.tick(40)
