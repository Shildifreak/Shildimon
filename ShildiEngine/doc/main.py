
URLs=["file:///home/joram/Programmierung/py4kids/Downloadmanager/Projektdata.txt",
      "http://shildimon.de/projekte/Projektdata.txt"]
FPS=8

import sys
import os

sep = os.path.sep
verzeichnis = sys.path[0]+sep

import urllib
import ConfigParser
import pygame
import pygame.locals as pgl

pygame.init()
window=pygame.display.set_mode()
windowwidth,windowheight=window.get_size()
clock=pygame.time.Clock()

pygame.draw.rect(window,(0,0,255),(windowwidth/2-103,windowheight/2-16,102,32))
pygame.draw.rect(window,(0,0,0),(windowwidth/2-102,windowheight/2-15,100,30))
pygame.draw.rect(window,(0,0,255),(windowwidth/2+1,windowheight/2-16,102,32))
pygame.draw.rect(window,(0,0,0),(windowwidth/2+2,windowheight/2-15,100,30))

font=pygame.font.Font(pygame.font.get_default_font(),20)
requiretext=font.render("This programm requires an internet connection.",1,(0,0,255))
oktext     =font.render("Ok",1,(0,0,255))
quittext   =font.render("Quit",1,(0,0,255))
window.blit(requiretext,((windowwidth-requiretext.get_width())/2,windowheight/2-50))
window.blit(oktext,((windowwidth-oktext.get_width())/2-50,(windowheight-oktext.get_height())/2))
window.blit(quittext,((windowwidth-quittext.get_width())/2+50,(windowheight-quittext.get_height())/2))

ende = False
while not ende:
    pygame.display.update()
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pgl.QUIT:
            ende = True
            permission = "denied"
        if event.type == pgl.MOUSEBUTTONDOWN:
            if pygame.Rect((windowwidth/2-102,windowheight/2-15,100,30)).collidepoint(event.pos):
                ende = True
                permission = "granted"
            if pygame.Rect((windowwidth/2+2,windowheight/2-15,100,30)).collidepoint(event.pos):
                ende = True
                permission = "denied"

test = None
if permission == "granted":
    for URL in URLs:
        if not test:
            try:
                test=urllib.urlopen(URL)
            except:
                print "failed loading infofile from",URL
if test:
    confi=ConfigParser.ConfigParser()
    confi.readfp(test)

    sections = confi.sections()
    print confi.sections()
    for section in confi.sections():
        print section
        print confi.items(section)

    def roundedrect(width,height,rounding,angle,color1,color2,text="",scale=2):
        width,height,rounding=width*scale,height*scale,rounding*scale
        drawing = pygame.Surface((width,height))
        drawing = drawing.convert_alpha()
        drawing.fill((0,0,0,0))
        d=4*scale
        pygame.draw.rect(drawing,color2,(0,rounding,width,height-2*rounding))
        pygame.draw.rect(drawing,color2,(rounding,0,width-2*rounding,height))
        pygame.draw.circle(drawing,color2,(rounding,rounding),rounding)
        pygame.draw.circle(drawing,color2,(width-rounding,rounding),rounding)
        pygame.draw.circle(drawing,color2,(rounding,height-rounding),rounding)
        pygame.draw.circle(drawing,color2,(width-rounding,height-rounding),rounding)
        pygame.draw.rect(drawing,color1,(d,rounding,width-2*d,height-2*rounding))
        pygame.draw.rect(drawing,color1,(rounding,d,width-2*rounding,height-2*d))
        pygame.draw.circle(drawing,color1,(rounding,rounding),rounding-d)
        pygame.draw.circle(drawing,color1,(width-rounding,rounding),rounding-d)
        pygame.draw.circle(drawing,color1,(rounding,height-rounding),rounding-d)
        pygame.draw.circle(drawing,color1,(width-rounding,height-rounding),rounding-d)
        passt=False
        for i in range(2*d,height):
            if not passt:
                size=height-i
                font=pygame.font.Font(pygame.font.get_default_font(),size)
                if font.size(text)[0]<width-2*d:
                    passt=True
        text=font.render(text,1,(0,0,0))
        print ((width-text.get_width())/2,(height-text.get_height())/2)
        drawing.blit(text,((width-text.get_width())/2,(height-text.get_height())/2))
        drawing=pygame.transform.rotozoom(drawing,angle,1./scale)
        return drawing

    slide = pygame.Surface((len(sections)*300,400))

    for i in range(len(sections)):
        x = i*300
        section=sections[i]
        status =confi.get(section,"status")
        slide.blit(roundedrect(200,250,40,0,(0,255,255),(0,128,128),section),(x+50,75))
        slide.blit(roundedrect(100,35,12,35,(0,255,0),(0,128,0),status),(x+20,45))
        #window.blit(roundedrect(40,40,20,0,(255,0,0),(128,0,0)),(200,100))

    window.fill((0,0,0))
    window.blit(slide,(0,(window.get_height()-slide.get_height())/2))

    ende = False
    while not ende:
        clock.tick(FPS)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                ende = True
    
pygame.quit()

#import zipfile
#filename=zipfile.ZipFile("/home/joram/test.txt.zip")
#filename.extractall("/home/joram/extract")

# status            delete
#       description
# update     download/play
