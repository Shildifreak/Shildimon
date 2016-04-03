# -*- coding: utf-8 -*-
#Die Anzeige eines Shildimonkampfes mittels pygame

FPS=16

import pygame
import pygame.locals as pgl
import math

#Damit jegliches Modul zum Darstellen des Kampfes die selben Variablen für die actionen hat
K_UP=pygame.K_UP
K_DOWN=pygame.K_DOWN
K_RIGHT=pygame.K_RIGHT
K_LEFT=pygame.K_LEFT
K_SPACE=pygame.K_SPACE
K_QUIT="ENDE"
K_1=pygame.K_1;K_2=pygame.K_2;K_3=pygame.K_3;K_4=pygame.K_4
K_5=pygame.K_5;K_6=pygame.K_6;K_7=pygame.K_7;K_8=pygame.K_8
K_9=pygame.K_9;K_0=pygame.K_0;
#Dictionary zur Speicherung ob Taste gedrückt ist:
key_state={K_UP:False,K_DOWN:False,K_RIGHT:False,K_LEFT:False,
           K_SPACE:False,
           K_1:False,K_2:False,K_3:False,K_4:False,K_5:False,
           K_6:False,K_7:False,K_8:False,K_9:False,K_0:False,}

class window(object):
    def __init__(self,width=800,height=480,fullscreen=False):
        # set up pygame
        pygame.init()
        self.mainClock = pygame.time.Clock()
        
        # set up the window
        self.WINDOWWIDTH = width
        self.WINDOWHEIGHT = height
        if fullscreen:
            self.windowSurface = pygame.display.set_mode(
                (self.WINDOWWIDTH, self.WINDOWHEIGHT),
                pygame.FULLSCREEN)
        else:
            self.windowSurface = pygame.display.set_mode(
                (self.WINDOWWIDTH, self.WINDOWHEIGHT),1,32)
        self.soure=None

    def setsource(self,source):
        self.source = source

    def drawsphere(self,pos3d,size,color):
        x3d, y3d, z3d = pos3d
        x =                      x3d + y3d/2
        y = self.WINDOWHEIGHT - (z3d + y3d/2)
        shadowx = x+z3d/2
        shadowy = self.WINDOWHEIGHT - (z3d + y3d)/2
        shadowrect=pygame.Rect(shadowx-size/2,shadowy,size*2,size)
        if z3d<0:
            z3d=0
        if z3d>-2*size:
            shadowcolor=[255-255/math.sqrt(z3d+1)]*3
            #shadowcolor=[255-255/(z3d+1)]*3
            pygame.draw.ellipse(self.windowSurface, shadowcolor, shadowrect)
            pygame.draw.circle(self.windowSurface, color, (int(x),int(y)), size)

    def drawshildimon(self,pos3d,size,name,direction):
        x3d, y3d, z3d = pos3d
        x =                      x3d + y3d/2
        y = self.WINDOWHEIGHT - (z3d + y3d/2)
        shadowx = x+z3d/2
        shadowy = self.WINDOWHEIGHT - (z3d + y3d)/2
        shadowrect=pygame.Rect(shadowx-size/2,shadowy,size*2,size)
        if z3d<0:
            z3d=0
        if z3d>-2*size:
            shadowcolor=[255-255/math.sqrt(z3d+1)]*3
            pygame.draw.ellipse(self.windowSurface, shadowcolor, shadowrect)
            num=str(int(-direction/22.5-4)%16).zfill(2)
            shildi=pygame.image.load(self.source+name+"/"+num+".png")
            shildi=pygame.transform.scale(shildi,(size*4,int(float(size*4)/shildi.get_height()*shildi.get_width())))
            self.windowSurface.blit(shildi,(int(x-size*2),int(y-size*2)))

    def drawrelaxtime(self,relaxtime):
        Rect = pygame.Rect(5,self.WINDOWHEIGHT-5-relaxtime*10,
                           10,relaxtime*10)
        pygame.draw.rect(self.windowSurface, (0,200,0), Rect)

    def update(self,seconds=1.0/FPS):
        for i in range(int(round(seconds*FPS))):
            pygame.display.update()
            self.mainClock.tick(FPS)

    def new_frame(self):
        self.windowSurface.fill((255,255,255))

    def get_key_state(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pgl.QUIT:
                return K_QUIT
            if event.type in (pgl.KEYDOWN,pgl.KEYUP):
                if event.key in key_state.keys():
                    key_state[event.key] = (event.type == pgl.KEYDOWN)
            #if event.type == pgl.MOUSEBUTTONUP:
            #if event.type == pgl.MOUSEMOTION:
        return [key for key in key_state.keys() if key_state[key]]

if __name__=="__main__":
    import time
    size=10
    color=(255,0,0)
    color2=(0,0,255)
    Testwin = window()
    height=250
    t=time.time()
    for i in range(0,1000,2):
        z=i%height*(i%(height*2)>height)+\
          (height-i%height)*(i%(height*2)<=height)
        pos3d=(100,400,z)
        Testwin.windowSurface.fill((255,255,255))
        Testwin.drawsphere(pos3d,size,color)
        Testwin.drawrelaxtime(time.time()-t)
        pygame.display.update()
    print "FPS", 500/(time.time()-t)
    t=time.time()
    for i in range(0,1000,1):
        x=math.sin(i/50.)*100+200
        y=math.cos(i/50.)*100+300
        pos3d=(x,y,0)
        Testwin.windowSurface.fill((255,255,255))
        Testwin.drawsphere(pos3d,size,color)

        x=math.cos(i/50.)*100+200
        y=math.sin(i/50.)*100+300
        pos3d=(x,y,20)
        Testwin.drawsphere(pos3d,size,color2)

        Testwin.drawrelaxtime(time.time()-t)
        pygame.display.update()
    print "FPS", 1000/(time.time()-t)
    #Testwin.update(3)
    pygame.quit()
