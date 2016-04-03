#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2008 Günter Milde.
#             Released  without warranties or conditions of any kind
#             under the terms of the Apache License, Version 2.0
# 	      http://www.apache.org/licenses/LICENSE-2.0
# :Id: $Id:  $

# : xturtle_png_shapes.py
# ============================================================

import PIL.Image, PIL.ImageTk

from random import random
from xturtle import *
from time import sleep

rahmen=Turtle()
rahmen.setup(1.0,1.0)
rahmen.pu()
rahmen.bk(150)
rahmen.pd()
for i in range(4):
    rahmen.color("grey80")
    rahmen.fd(5)
    rahmen.color("red")
    rahmen.fd(5)
rahmen.pu()
rahmen.color("black")
rahmen.goto(-200,300)
rahmen.pd()
rahmen.goto(-200,-150)
rahmen.goto(200,-150)
rahmen.goto(200,300)
rahmen.pu()
rahmen.hideturtle()


image1 = PIL.Image.open("/home/joram/SuperTux/supertux/data/images/creatures/tux/small/stand-0.png")
image1 = image1.transpose(0)
photo1 = PIL.ImageTk.PhotoImage(image1)

image2 = PIL.Image.open("/home/joram/SuperTux/supertux/data/images/creatures/tux/small/stand-0.png")
photo2 = PIL.ImageTk.PhotoImage(image2)

myshape1 = Shape("image", photo1)
myshape2 = Shape("image", photo2)

addshape("links", myshape1)
addshape("rechts", myshape2)

shape("links")
richtung="links"

def wechselimage():
    global richtung
    if richtung=="links":
        richtung="rechts"
        shape("rechts")
    else:
        richtung="links"
        shape("links")

#speed(1)
penup()


ende=False
def beend():
    global ende
    ende=True

def spur():
    if isdown():
        up()
        clear()
    else:
        down()

def main():
    global schreiber,richtung
    try:
        schreiber
    except:
        schreiber=Turtle()
        schreiber.hideturtle()
    schreiber.clear()
    clear()
    goto(-20,-100)
    shape("links")
    richtung="links"
    ende=False
    onkey(spur,"t")
    onkey(beend,"space")
    listen()
    anfangsspeed=(-3.0,9.0)
    speed=anfangsspeed
    punkte=0
    getpunkt=False
    
    while not ende:
        tracer(False)
        goto(pos()[0]+speed[0],pos()[1]+speed[1])
        speed=(speed[0],speed[1]-0.2)
        #auf boden Aufprellen
        if pos()[1]<-125:
            speed=(speed[0],random()*anfangsspeed[1])
            getpunkt=False
        #von wand abprellen
        if pos()[0]<-180 or pos()[0]>180:
            speed=(speed[0]*-1,speed[1])
            wechselimage()
        #an hinderniss anstoßen
        if pos()[1]<-85 and pos()[0]in(-2,-1,-0,1,2):
            schreiber.write("ouch",font=("Arial", 20, "normal"))
            sleep(1)
            break
        #über hinderniss drüberspringen
        if pos()[0]in(-2,-1,0,1,2)and getpunkt==False:
            punkte+=1
            getpunkt=True
        tracer(True)
        fd(0)
        sleep(0.01)

    schreiber.write("\t"+str(punkte),font=("Ansi",30))
    onkey(main,"space")

if __name__=="__main__":
    onkey(main,"space")
    listen()
#bye()
