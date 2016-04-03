#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import pygame, sys, random#, pygame.font
import pygame.locals as pgl
import time, math
from os import sep as sep
from string import printable
printable=unicode(printable.replace("\n","").replace("\r","").replace("\t",""))+u"ÄÖÜäöüß"

class player(object):
    def __init__(self,landschaft,path,northimage,eastimage,southimage,westimage):
        self.landschaft = landschaft
        self.path=path
        self.standartimagepaths = [northimage,eastimage,southimage,westimage]
        self.northimage = pygame.image.load(path+northimage)
        self.eastimage  = pygame.image.load(path+eastimage)
        self.southimage = pygame.image.load(path+southimage)
        self.westimage  = pygame.image.load(path+westimage)
        self.northcloth = None
        self.eastcloth  = None
        self.southcloth = None
        self.westcloth  = None
        self.cloth = self.southcloth
        self.Image = self.southimage
        self.direction = "south"
        self.Rect = pygame.Rect(
            (landschaft.WINDOWWIDTH-self.Image.get_size()[0])/2.0,
            (landschaft.WINDOWHEIGHT-self.Image.get_size()[1])/2.0-20,
            50,50)
        self.pos = self.Rect.topleft[0],self.Rect.topleft[1]
        self.kleidung=[]
        self.trageitems=[]

    def prepare_update(self,level=0,force_update="dummi"):
        self.landschaft.changedrects.append(self.Rect)
    
    def update(self):
        i ={"north":0,"east":1,"south":2,"west":3}[self.direction]+\
           {"oben":0,"rechts":3,"unten":2,"links":1}[self.landschaft.blickrichtung]
        i = i%4
        self.cloth={0:self.northcloth,1:self.eastcloth,
                    2:self.southcloth,3:self.westcloth}[i]
        self.Image={0:self.northimage,1:self.eastimage,
                    2:self.southimage,3:self.westimage}[i]
        self.landschaft.map.blit(self.Image, self.Rect)
        if self.cloth:
            #self.Clothrect=self.Rect.copy()
            self.Clothrect=pygame.Rect(self.Rect)
            self.Clothrect.y=self.Rect.y-5
            self.landschaft.map.blit(self.cloth,self.Clothrect)

    def reaktionslaufen(self, action):
        if action[:6]=="shape(":
            if action[6:-1] == "":
                northimage,eastimage,southimage,westimage\
                    = self.standartimagepaths
            else:
                northimage,eastimage,southimage,westimage\
                    = action[6:-1].split(",")
            self.northimage = pygame.image.load(self.path+northimage)
            self.eastimage  = pygame.image.load(self.path+eastimage)
            self.southimage = pygame.image.load(self.path+southimage)
            self.westimage  = pygame.image.load(self.path+westimage)
            self.Rect = pygame.Rect(
            (self.landschaft.WINDOWWIDTH-self.Image.get_size()[0])/2.0,
            (self.landschaft.WINDOWHEIGHT-self.Image.get_size()[1])/2.0-20,
            50,50)
            self.pos = self.Rect.topleft
            return "none"

    def looknorth(self):
        self.direction = "north"

    def lookeast(self):
        self.direction = "east"

    def looksouth(self):
        self.direction = "south"

    def lookwest(self):
        self.direction = "west"

    def setitems(self,items,itemdir):
        import itemfuncs
        kleidung = []
        def findeitems(inventar,liste):
            for key in inventar.keys():
                if inventar[key][1] != {}:
                    liste=findekleidung(inventar[key][1],liste)
                liste.append(inventar[key][0][:-1])
            return liste
        kleidungsslots = {}
        for a,b in items.items():
            if a in [(6,2), (2,6), (6,6), (10,6), (6,10), (6,14),(7,14), (6,15),(7,15), (5,16),(6,16),(7,16),(8,14),(9,14),(8,15),(9,15),(8,16),(9,16),(10,16)]:
                kleidungsslots[a]=b
        #kleidungsslots = {a:b for a,b in spieler.items.items() if a in [(7,1), (1,6), (7,7), (13,6),(1,14), (7,13), (13,14)]}
        self.kleidung=findeitems(kleidungsslots,kleidung)
        #print self.kleidung
        trageitems = []
        trageslots = {}
        for a,b in items.items():
            if a in [(6,2), (2,6), (6,6), (10,6), (6,10), (6,14),(7,14), (6,15),(7,15), (5,16),(6,16),(7,16),(8,14),(9,14),(8,15),(9,15),(8,16),(9,16),(10,16),(15,12),(23,12)]:
                trageslots[a]=b
        self.trageitems=findeitems(trageslots,trageitems)
        print "trageitems:",self.trageitems
        
        self.northcloth = pygame.Surface((self.Rect.width,self.Rect.height)).convert_alpha()
        self.northcloth.fill((0,0,0,0))
        self.eastcloth  = pygame.Surface((self.Rect.width,self.Rect.height)).convert_alpha()
        self.eastcloth.fill((0,0,0,0))
        self.southcloth = pygame.Surface((self.Rect.width,self.Rect.height)).convert_alpha()
        self.southcloth.fill((0,0,0,0))
        self.westcloth  = pygame.Surface((self.Rect.width,self.Rect.height)).convert_alpha()
        self.westcloth.fill((0,0,0,0))
        for item in self.kleidung:
            x,y=0,0
            self.northcloth.blit(pygame.image.load(itemdir+item+sep+"north.png"),(x,y))
            self.eastcloth.blit(pygame.image.load(itemdir+item+sep+"east.png"),(x,y))
            self.southcloth.blit(pygame.image.load(itemdir+item+sep+"south.png"),(x,y))
            self.westcloth.blit(pygame.image.load(itemdir+item+sep+"west.png"),(x,y))
        self.landschaft.bonuslights=[]
        for item in self.trageitems:
            light=itemfuncs.getdefaults(item,itemdir).get("lightbonus",None)
            if light:
                self.landschaft.bonuslights.append(
                    (int(light.split(",")[0]),int(light.split(",")[1])))

class Simple_objekt(object):
    def __init__(self,data,pos,landschaft):
        self.data = data
        self.landschaft = landschaft
        self.imgcmd = {}
        self.img    = {}
        
        # Commands laden
        for layer in ("background","file","forperson"):
            if data.has_key(layer):
                self.imgcmd[layer] = data[layer]
                self.img[layer] = "transparent.png"

        self.startpos = list(pos)
        self.pos = list(pos)
        #print data
        self.level=int(data.get("level",0))
        self.height=int(data.get("height",1))
        self.Rect = pygame.Rect(pos[0],pos[1]-int(self.level)*10,50,50)
        #self.prepare_update(0,True)
        #self.update()
        
    def move(self,x,y):
        self.pos[0]+=x; self.pos[1]+=y

    def goto(self,x,y):
        self.pos[0]=self.startpos[0]+x
        self.pos[1]=self.startpos[1]+y

    def prepare_update(self,level=0,force_update=False,update_imgs=True):
        x,y=self.pos[0],self.pos[1]
        x,y=x-self.landschaft.WINDOWWIDTH/2+25,y-self.landschaft.WINDOWHEIGHT/2+25
        x,y={"oben":(x,y),"rechts":(y,-x),"unten":(-x,-y),"links":(-y,x)
             }[self.landschaft.blickrichtung]
        x,y=x+self.landschaft.WINDOWWIDTH/2-25,y+self.landschaft.WINDOWHEIGHT/2-25
        self.Rect.topleft = [x,y-int(self.level-level)*10]
        self.force_update = force_update
        if not self.Rect.colliderect(pygame.Rect(0,0,800,480)):
            return
        self.Blitrect = self.Rect
        self.Cliprect = pygame.Rect(0,0,self.Rect.height,self.Rect.width)
        if self.Rect.collidelist(self.landschaft.changedrects)!=-1 and not self.force_update:
            self.force_update = True
            collidelist=self.Rect.collidelistall(self.landschaft.changedrects)
            self.Blitrect=self.Rect.clip(self.landschaft.changedrects[collidelist[0]])
            for i in collidelist[1:]: #nicht range
                colliderect=self.Rect.clip(self.landschaft.changedrects[i])
                self.Blitrect=self.Blitrect.union(colliderect)
            self.Cliprect=pygame.Rect(self.Blitrect.x-self.Rect.x,
                                      self.Blitrect.y-self.Rect.y,
                                      self.Blitrect.width,self.Blitrect.height)
        if update_imgs:
            for layer in ("background","file","forperson"):
                if self.imgcmd.has_key(layer) and\
                   (not self.imgcmd[layer].endswith(".png") or self.img[layer]=="transparent.png"):
                    newimg=self.landschaft.reaktionslaufen(self.imgcmd[layer])
                    if newimg != self.img[layer]:
                        self.img[layer] = newimg
                        self.force_update = True
                    if newimg not in self.landschaft.images.keys():
                        try:
                            self.landschaft.images[newimg]=pygame.image.load(
                            self.landschaft.imagepaths[newimg])
                        except:
                            print "Error while loading:",newimg
                            self.landschaft.images[newimg]=None
        if self.force_update:
            self.landschaft.changedrects.append(self.Blitrect)

    def update(self):
        if self.force_update:
            for layer in ("background","file"):
                if self.img.has_key(layer):
                    if self.img[layer]!="transparent.png":
                        if self.landschaft.images[self.img[layer]]:
                            self.landschaft.map.blit(
                                self.landschaft.images[self.img[layer]],
                                self.Blitrect,self.Cliprect)
    
    def fgupdate(self):
        #Rects und self.force_update = schon von update() initialisiert
        if not self.Rect.colliderect(pygame.Rect(0,0,800,480)):
            return
        layer = "forperson"
        if self.img.has_key(layer): #and self.force_update
            if self.img[layer]!="transparent.png":
                if self.landschaft.images[self.img[layer]]:
                    self.landschaft.map.blit(
                        self.landschaft.images[self.img[layer]],self.Rect)
                        #self.Blitrect,self.Cliprect)
                    #self.landschaft.changedrects.append(self.Blitrect)



class Complex_objekt(object):
    def __init__(self,data,name,landschaft):
        self.data = data
        self.name = name
        #print data
        self.landschaft = landschaft
        self.Image = pygame.image.load(
            self.landschaft.objektpaths[data["bild"]])
        self.Rect = self.Image.get_rect()
        self.xpos = int(self.data["position"].split(",")[0][1:])*50
        self.ypos = int(self.data["position"].split(",")[1][:-1])*50
        self.startpos = [self.xpos,self.ypos]
        self.pos = [self.xpos,self.ypos]
        self.Rect.topleft = self.pos

    def move(self,x,y):
        self.pos[0]+=x; self.pos[1]+=y
        self.Rect.topleft = self.pos

    def goto(self,x,y):
        self.pos[0]=self.startpos[0]+x
        self.pos[1]=self.startpos[1]+y
        self.Rect.topleft = self.pos

    def prepare_update(self,level=0,force_update="dummi"):
        x,y=self.pos
        x,y=x-self.landschaft.WINDOWWIDTH/2+25,y-self.landschaft.WINDOWHEIGHT/2+25
        x,y={"oben":(x,y),"rechts":(y,-x),"unten":(-x,-y),"links":(-y,x)
             }[self.landschaft.blickrichtung]
        x,y=x+self.landschaft.WINDOWWIDTH/2-25,y+self.landschaft.WINDOWHEIGHT/2-25
        self.Rect.topleft=(x,y)
        self.landschaft.changedrects.append(self.Rect)

    def update(self):
        self.landschaft.map.blit(self.Image, self.Rect)

    def reaktionslaufen(self, action):
        #print "reactionrun:",action
        #print action[:6]
        if action[:6]=="shape(":
            #print action[6:-1]
            if action[6:-1]!=self.data["bild"]:
                self.data["bild"]=action[6:-1]
                self.Image = pygame.image.load(
                    self.landschaft.objektpaths[self.data["bild"]])
                self.Rect = self.Image.get_rect()
                self.Rect.topleft=self.pos
            return "none"
        elif action[:5]=="move(":
            x = int(action[5:-1].split(",")[0])*50
            y = int(action[5:-1].split(",")[1])*50
            self.landschaft.cobjektsbypos.pop((((self.xpos+25-self.landschaft.size[0]/2)*-1)/50,
                            (self.ypos+25-self.landschaft.size[1]/2)/50))
            self.xpos+=x
            self.ypos+=y
            self.startpos=[self.xpos,self.ypos]
            self.landschaft.cobjektsbypos[(((self.xpos+25-self.landschaft.size[0]/2)*-1)/50,
                            (self.ypos+25-self.landschaft.size[1]/2)/50)]=self
            self.move(x,y)
            return "none"
        elif action[:9]=="setlight(":
            self.data["light"]=action[9:-1]
        
class pygame_landschaft():
    def __init__(self,datafile,landschaftsfile=None,title="MCGEM",width=400,height=400,fullscreen=False,screenobject=None):
        print("initialising pygame_landschaft")
        self.configleser = ConfigParser.ConfigParser()
        self.datafile = datafile+"Landschaftssegmente"+os.sep
        self.fontfile = datafile[:datafile[:datafile.rfind(sep)].rfind(sep)+1]+"Fonts%sArtifika.ttf" %sep
        #print self.fontfile
        self.textbgfile = datafile+"other"+os.sep+"redefenster.gif"
        self.pos = (0,0)
        self.landschaftsfile = landschaftsfile
        self.landschaftsname = None
        self.simpleobjekts = []
        self.complexobjekts = {}
        self.kaestcheneigenschaften = {}
        self.kaestchenitems = {}
        self.cobjektsbypos = {}
        self.adsurface = None
        self.light = 255 #of 0-255 or -1 ("daylight")
        self.bonuslights = []
        self.playerlight = (100,255)
        self.textinput = ""
        self.FULLSCREEN = fullscreen
        self.cyclecount = 0
        self.changedrects = []
        self.textlines = [""]
        self.textpointer = 0
        self.showtext = False
        self.crodespeicher = {}
        self.level = 0
        self.movetime = 0
        self.blickrichtung = "oben"
        self.letzteblickrichtung = ""

        def reaktionslaufen (x):
            return x
        self.reaktionslaufen = reaktionslaufen

        # set up pygame
        pygame.init()
        self.mainClock = pygame.time.Clock()
        self.fpstimelist = [0]*9+[time.time()]
        
        # set up the window
        self.WINDOWWIDTH = width
        self.WINDOWHEIGHT = height
        if screenobject:
            self.windowSurface = screenobject
        else:
            if fullscreen:
                self.windowSurface = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT),pygame.FULLSCREEN)
            else:
                self.windowSurface = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT),1,32)
        self.title=title
        pygame.display.set_caption(self.title)
        self.map = self.windowSurface.copy()

        # Bindingslisten
        self._keydown_bindings = {}
        self._keyup_bindings = {}
        self._keylist_bindings = {}
        self._mousedown_bindings = {}
        self._strg = False
        self._keylist = []

        self.imagepaths = {}
        self.images={}
        self.player = None
        def lies(path):
            for datei in os.listdir(path):
                if os.path.isdir(path+datei):
                    lies(path+datei+os.path.sep)
                else:
                    self.imagepaths[datei] = path+datei
            #return self.imagepaths
        dfs = lies(self.datafile)
        #print dfs
        self.objektpaths = {}
        self.player = None
        def lies(path):
            for datei in os.listdir(path):
                if os.path.isdir(path+datei):
                    lies(path+datei+os.path.sep)
                else:
                    self.objektpaths[datei] = path+datei
            #return self.objektpaths
        dfs = lies(self.datafile[:self.datafile[:-1].rindex(os.path.sep)+1])
        #print dfs

        if landschaftsfile != None:
            self.landschaft(landschaftsfile)

    def landschaft(self,landschaftsfile):
        self.pos = (0,0)
        self.intpos = (0,0)
        self.simpleobjekts=[]
        self.complexobjekts={}
        self.kaestcheneigenschaften={}
        self.kaestchenitems={}
        self.cobjektsbypos={}

        self.landschaftsfile = landschaftsfile
        # configleser leeren
        for i in self.configleser.sections():
            self.configleser.remove_section(i)
        # configleser neu einlesen
        self.configleser.read(self.landschaftsfile)
        #print self.configleser.sections()

        self.eigenschaften = dict(self.configleser.items("Eigenschaften"))
        self.size = (int(self.eigenschaften["size"][1:-1].split(",")[0])*50,
                     int(self.eigenschaften["size"][1:-1].split(",")[1])*50)
        self.landschaftsname=self.eigenschaften["name"]
        self.light= int(self.eigenschaften.get("light",255))

        for section in self.configleser.sections():
            #print section
            if section == "Eigenschaften":
                pass
            elif section[:6]=="objekt":
                objekt = Complex_objekt(dict(self.configleser.items(section)),section[7:],self)
                #print objekt.data
                xpos = int(objekt.data["position"].split(",")[0][1:])*50
                ypos = int(objekt.data["position"].split(",")[1][:-1])*50
                #print xpos,ypos
                self.complexobjekts[section[7:]] = objekt
                self.cobjektsbypos[(((xpos+25-self.size[0]/2)*-1)/50,
                            (ypos+25-self.size[1]/2)/50)] = self.complexobjekts[section[7:]]
            else:
                tile = dict(self.configleser.items(section))
                pos = (int(section.split(",")[0])*50,
                       int(section.split(",")[1])*50)
                #Shildimonkaestcheneigenschaftenformat:
                #  nullpunkt in mitte,seitenverkehrt(horizontal+vertikal)
                self.kaestcheneigenschaften[(((pos[0]+25-self.size[0]/2)*-1)/50,
                            (pos[1]+25-self.size[1]/2)/50)] = tile["action"]
                self.kaestchenitems[(((pos[0]+25-self.size[0]/2)*-1)/50,
                            (pos[1]+25-self.size[1]/2)/50)] = tile
                self.simpleobjekts.append(Simple_objekt(tile,pos,self))
        self.windowSurface.fill((0,0,0))
        self.map.fill((0,0,0))

    def update(self,adsurface=None,show=True,objactfunc=None,force_update=False):
        if self.blickrichtung != self.letzteblickrichtung:
            self.letzteblickrichtung = self.blickrichtung
            force_update = True
        self.cyclecount+=1
        tlist=[]
        t=time.time()
        if adsurface==None:
            adsurface=self.adsurface
        elif adsurface==False:
            adsurface=None
        else:
            self.adsurface=adsurface
        if objactfunc and self.reaktionslaufen != objactfunc:
            self.reaktionslaufen=objactfunc
            for img,path in self.imagepaths.items():  #M# ???
                if path == None:
                    self.imagepaths.pop(img)
        for obj in self.complexobjekts.values():
            #print obj.data["loopfunction"]
            self.reaktionslaufen(obj.data["loopfunction"])
        #herausbekommen, welches objekt am nächsten zu (0,0) ist
        nearest=(1000,0) #(maximaler Sichtradius, Ausgangshöhe)
        for objekt in self.simpleobjekts:
            if abs(objekt.pos[0]+25-self.WINDOWWIDTH/2
                   )+abs(objekt.pos[1]+25-self.WINDOWHEIGHT/2)<nearest[0]:
                nearest=(abs(objekt.pos[0]+25-self.WINDOWWIDTH/2
                   )+abs(objekt.pos[1]+25-self.WINDOWHEIGHT/2),objekt.level)
        self.level=nearest[1]
        #print nearest
        tlist.append(time.time()-t)
        t = time.time()

        self.objektelist = []
        for objekt in self.simpleobjekts + self.complexobjekts.values()+[self.player]:
            if objekt:
                typ={player:2,Complex_objekt:1,Simple_objekt:0}[type(objekt)]
                x,y=objekt.pos
                y={"oben":y,"rechts":-x,"unten":-y,"links":x}[self.blickrichtung]
                if typ != 2:
                    y-=40
                y=int(y/50)*50
                self.objektelist.append((y,typ,objekt))
#        if self.player:
#            self.objektelist.append((self.player.y,2,self.player))
        self.objektelist.sort()

        internalcyclecount=self.cyclecount%16                
        for y,typ,objekt in self.objektelist[::-1]+self.objektelist:
            if not force_update:
                objekt.prepare_update(self.level,internalcyclecount==0)
            else:
                objekt.prepare_update(self.level,True)
            internalcyclecount+=1
            if internalcyclecount > 15:
                internalcyclecount-=16

        c_obj_cache=[]
        s_obj_cache=[]
        lasty=None
        for y,typ,objekt in self.objektelist:
            if y != lasty:
                for o in s_obj_cache:
                    o.update()
                for o in c_obj_cache:
                    o.update()
                for o in s_obj_cache:
                    o.fgupdate()
                c_obj_cache=[]
                s_obj_cache=[]
            if typ == 0:
                s_obj_cache.append(objekt)
            else:
                c_obj_cache.append(objekt)
            lasty = y
        for o in s_obj_cache:
            o.update()
        for o in c_obj_cache:
            o.update()
        for o in s_obj_cache:
            o.fgupdate()
        
        tlist.append(time.time()-t)
        t = time.time()
        if show:
            #mx,my = self.WINDOWWIDTH/2, self.WINDOWHEIGHT/2
            #x,y = self.pos
            #b,h = self.size
            #b1 = mx-x; b2 = b-b1
            #h1 = my-y; h2 = h-h1
            #x,y,b,h = {"oben":(x,y,b,h),"rechts":(mx-h1,my-b2,h,b),
            #         "unten":(mx-b2,my-h2,b,h),"links":(mx-h2,my-b1,h,b)
            #        }[self.blickrichtung]
            #self.windowSurface.fill((0,0,0)) #Verbraucht relativ viel Leistung
            #self.windowSurface.blit(self.map,(x,y),(x,y,b,h)) #M#
            self.windowSurface.blit(self.map,(0,0))
            self.decoration(adsurface)
            pygame.display.update()
            
        tlist.append(time.time()-t)
        #print self.changedrects
        self.changedrects=[]
        return tlist

    def decoration(self,adsurface=None):
        #if self.player:
        #    self.player.update()
        #for objekt in self.simpleobjekts + self.complexobjekts.values():
        #    objekt.fgupdate(self.level)
        if self.light != 255:
                lightmap = pygame.Surface((800,480),pgl.SRCALPHA)
                #lightmap = lightmap.convert_alpha(self.windowSurface)
                lightmap.fill((0,0,0,255-self.light))
                lights = [(self.playerlight[0],self.playerlight[1],
                           (self.WINDOWWIDTH/2.0,self.WINDOWHEIGHT/2.0))]
                for i in self.bonuslights:
                    lights.append((i[0],i[1],(self.WINDOWWIDTH/2.0,self.WINDOWHEIGHT/2.0)))
                for objekt in self.simpleobjekts:
                    if objekt.data.has_key("light"):
                        level = int(objekt.data["light"].split(",")[0])
                        radius= int(objekt.data["light"].split(",")[1])
                        pos = (objekt.pos[0]+25,objekt.pos[1]-int(objekt.level)*10+25)
                        lights.append((level,radius,pos))
                for objekt in self.complexobjekts.values():
                    if objekt.data.has_key("light"):
                        level = int(objekt.data["light"].split(",")[0])
                        radius= int(objekt.data["light"].split(",")[1])
                        pos = (objekt.pos[0]+25,objekt.pos[1]+25)
                        lights.append((level,radius,pos))
                lights.sort()
                for level,radius,(x,y) in lights:
                    if level > self.light:
                        #testi = pygame.Surface((radius*2,radius*2),pgl.SRCALPHA)
                        #pygame.draw.circle(testi,(0,0,0,255-level),(radius,radius),radius)
                        #lightmap.blit(testi,(x-radius,y-radius))
                        pygame.draw.circle(lightmap,(0,0,0,255-level),(int(x),int(y)),radius)
                self.windowSurface.blit(lightmap,(0,0))
        if adsurface:
            self.windowSurface.blit(adsurface,(0,0))
        fpsaverage=len(self.fpstimelist)/(self.fpstimelist[-1]-self.fpstimelist.pop(0))
        self.fpstimelist.append(time.time())
        font = pygame.font.Font(self.fontfile, 20)
        fpsimage = font.render(str(int(fpsaverage+0.5)), 1, (255, 0, 0))
        self.windowSurface.blit(fpsimage, fpsimage.get_rect(x=self.WINDOWWIDTH-25,y=0))
        if self.showtext:
            self.blittext()
        if self.textinput:
            self.blittextinput()

    def quit(self):
        pygame.quit()
        del(self)

    def onkey(self, func, key):
        """Bind an action to a key press event"""
        if type(key) in (str,unicode) and len(key) == 1:
            if key in printable:
                key = key
            else:
                key = ord(key)
        self._keydown_bindings[key] = func
        
    def onkeyrelease(self, func, key):
        """Bind an action to a key release event"""
        if type(key) == str and len(key) == 1:
            key = ord(key)
        self._keyup_bindings[key] = func

    def onkeylist(self, func, keylist):
        """Bind an action to a list of keys pressed while Strg hold"""
        for i in range(len(keylist)):
            if type(keylist[i]) == str and len(keylist[i]) == 1:
                keylist[i] = ord(keylist[i])
        self._keylist_bindings[tuple(keylist)] = func

    def onclick(self, func, button):
        """Bind an action to a mouseclick event"""
        self._mousedown_bindings[button] = func
    
    def speed(self,speed):
        self.speed = speed

    def move(self,x,y,FPS=15,speed=100):
        self.movetime=time.time()
        if (x==0) or (y==0):
            dt=abs(x+y)/float(speed)
        else:
            dt=math.sqrt(x**2+y**2)/float(speed)
        startpos=[i for i in self.pos]
        while time.time()-self.movetime<=dt:
            teil=(time.time()-self.movetime)/dt
            self.pos=(int(startpos[0]+x*teil),int(startpos[1]-y*teil))
            self.scrollscreen()
            for objekt in self.simpleobjekts + self.complexobjekts.values():
                objekt.goto(*self.pos)
            self.loop()
            self.update()
            self.mainClock.tick(FPS)
        self.pos=(startpos[0]+x,startpos[1]-y)
        self.scrollscreen()
        for objekt in self.simpleobjekts + self.complexobjekts.values():
            objekt.goto(*self.pos)
        self.loop()
        self.update()

    def goto(self,x,y):
        x = x + self.WINDOWWIDTH/2.0-self.size[0]/2.0
        y =-y + self.WINDOWHEIGHT/2.0-self.size[0]/2.0
        a = x - self.pos[0]
        b = y - self.pos[1]
        self.pos = (x,y)
        self.scrollscreen()
        for objekt in self.simpleobjekts + self.complexobjekts.values():
            objekt.move(a,b)

    def scrollscreen(self):
        inta=int(self.pos[0]-self.intpos[0])
        intb=int(self.pos[1]-self.intpos[1])
        self.intpos = (self.intpos[0]+inta,self.intpos[1]+intb)
        inta,intb = {"oben":(inta,intb),"rechts":(intb,-inta),
                     "unten":(-inta,-intb),"links":(-intb,inta)
                    }[self.blickrichtung]
        if self.player:
            self.changedrects.append(self.player.Rect)
            #pygame.draw.rect(self.map,(0,0,0),self.player.Rect)
        try:
            self.map.scroll(inta,intb) #pygame1.9Feature
        except:
            self.map.blit(self.map,(inta,intb))
        self.changedrects=[rect.move(inta,intb) for rect in self.changedrects]
        if inta>0:
            rect=pygame.Rect(0,0,inta,self.WINDOWHEIGHT)
            self.changedrects.append(rect)
            pygame.draw.rect(self.map,(0,0,0),rect)
        if inta<0:
            rect=pygame.Rect(self.WINDOWWIDTH+inta,0,-inta,self.WINDOWHEIGHT)
            self.changedrects.append(rect)
            pygame.draw.rect(self.map,(0,0,0),rect)
        if intb>0:
            rect=pygame.Rect(0,0,self.WINDOWWIDTH,intb)
            self.changedrects.append(rect)
            pygame.draw.rect(self.map,(0,0,0),rect)
        if intb<0:
            rect=pygame.Rect(0,self.WINDOWHEIGHT+intb,self.WINDOWWIDTH,-intb)
            self.changedrects.append(rect)
            pygame.draw.rect(self.map,(0,0,0),rect)
            
    def tellpos(self):
        return (self.pos[0]-self.WINDOWWIDTH/2.0+self.size[0]/2.0,
                -self.pos[1]+self.WINDOWHEIGHT/2.0-self.size[1]/2.0)

    def showimage(self, imagepath):
        self.windowSurface.fill((0,0,0))
        image=pygame.image.load(imagepath)
        self.windowSurface.blit(image,(0,0))
        pygame.display.update()
        beenden=False
        while not beenden:
            for event in pygame.event.get():
                if event.type == pgl.QUIT:
                    beenden=True
                if event.type == pgl.KEYUP:
                    beenden=True
            pygame.display.update()

    def auswahl(self,liste,FPS=16):
        pointer = 0
        self.showtext = True
        if self.textlines[-1]!="":
            self.textlines.append("")
        self.textpointer = len(self.textlines)
        textpointerstart = self.textpointer
        for i in range(len(liste)):
            self.textlines.append(liste[i])
        x,y=self.WINDOWWIDTH/2.0-165, self.WINDOWHEIGHT-148-50
        beenden = False
        downpressed=False
        uppressed=False
        speed = 0
        pygame.event.get()
        while not beenden:
            for event in pygame.event.get():
                if event.type == pgl.QUIT:
                    beenden=True
                if event.type in (pgl.KEYDOWN, pgl.KEYUP):
                    if event.key == pgl.K_PAGEUP:
                        uppressed = event.type == pgl.KEYDOWN
                    elif event.key == pgl.K_PAGEDOWN:
                        downpressed = event.type == pgl.KEYDOWN
                    elif event.type == pgl.KEYDOWN:
                        if event.key == pgl.K_RETURN:
                            beenden=True
                        else:
                            pointer+=(event.key==pgl.K_DOWN)-(event.key==pgl.K_UP)
                            pointer = pointer % len(liste)
                            if textpointerstart-self.textpointer+pointer<0:
                                self.textpointer=textpointerstart+pointer
                            if textpointerstart-self.textpointer+pointer>4:
                                self.textpointer=textpointerstart+pointer-4
            speed=speed*0.9
            if uppressed:
                speed-=0.1
            elif downpressed:
                speed+=0.1
            self.textpointer+=speed
            self.mainClock.tick(FPS)
            self.update(show=False)
            a,b=self.pos
            #self.map.blit(self.windowSurface,(0,0))
            #self.map.blit(self.windowSurface,(a,b),(a,b,self.size[0],self.size[1])) #M# klappt mit Landschaft drehen nicht mehr
            self.windowSurface.blit(self.map,(0,0))
            self.decoration()
            yd=textpointerstart*22-self.textpointer*22+pointer*22
            if -22 < yd < 110:
                pointlist=[(x,y+yd+00),(x+5,y+yd+05),
                           (x,y+yd+10),(x-5,y+yd+05)]
                pygame.draw.polygon(self.windowSurface,(0,0,0),pointlist)
            pygame.display.update()
            #self.windowSurface.blit(self.map,(a,b),(a,b,self.size[0],self.size[1])) #M# klappt mit Landschaft drehen nicht mehr
        self.showtext = False
        return pointer

    def text(self,text,speed=0.5,FPS=16):
        self.showtext = True
        if self.textlines[-1]!="":
            self.textlines.append("")
            self.textpointer += 2
        if not text.startswith("/c"):
            self.textpointer = len(self.textlines)
        else:
            text=text[2:]
        textpointersoll = self.textpointer
        self.textlines.append("")
        font = pygame.font.Font(self.fontfile, 20)
        returnpressed=False
        pygame.event.get()
        scrollspeed=0
        counter=0
        slash=False
        for b in text:
            waiting=False
            if slash:
                slash=False
                b="/"+b
            elif b == "/":
                slash=True
                b = ""
            if self.textlines[-1] == "":
                x = 0
            else:
                x = sum([i[4] for i in list(font.metrics(self.textlines[-1]))])
            if x>280 or b in ("\n","/n") or (x>240 and b in " -"):
                if b not in ("\n"," ","/n"):
                    self.textlines[-1]+="-"
                if b in ("/n","\n","/w"):
                    waiting=True
                self.textlines.append("")
                if len(self.textlines)-textpointersoll>5:
                    textpointersoll+=1
                    #if textpointersoll-self.textpointer>1:
                        #self.textpointer=textpointersoll-1
                self.mainClock.tick(FPS)
                self.update()
                if b not in ("\n"," ","/n","-"):
                    self.textlines[-1] += b
            else:
                self.textlines[-1] += b
            while True:
                for event in pygame.event.get():
                    if event.type==pgl.KEYDOWN:
                        waiting = False
                        if event.key==pgl.K_RETURN:
                            returnpressed=True
                    if event.type==pgl.KEYUP:
                        if event.key==pgl.K_RETURN:
                            returnpressed=False
                if not waiting:
                    break
            scrollspeed*=0.5
            if textpointersoll-self.textpointer>0.6:
                scrollspeed+=0.05
            elif textpointersoll-self.textpointer>0.1:
                scrollspeed+=0.01
            else:
                scrollspeed=0
                self.textpointer=textpointersoll
            self.textpointer+=scrollspeed
            if not returnpressed:
                counter+=speed
                while counter>1:
                    counter-=1
                    self.mainClock.tick(FPS)
                    self.update()
        self.waitforkey(FPS)
        self.showtext=False

    def blittext(self):
        font = pygame.font.Font(self.fontfile, 20)
        textlayer = pygame.Surface((390,198))
        textlayer = textlayer.convert_alpha()
        textlayer.fill((0,0,0,0))
        Rect = (self.WINDOWWIDTH/2.0-195, self.WINDOWHEIGHT-198-50)
        bgimage = pygame.image.load(self.textbgfile)
        textlayer.blit(bgimage,(0,0))
        for i in range(6):
            linenumber=int(self.textpointer)+i
            if 0 <= linenumber < len(self.textlines):
                line = font.render(self.textlines[linenumber], 1, (0, 0, 0))
                textlayer.blit(line, line.get_rect(x=40,y=(linenumber-self.textpointer)*22+40))
        self.windowSurface.blit(textlayer,Rect)        

    def blittextinput(self):
        font = pygame.font.Font(self.fontfile, 20)
        textlayer = pygame.Surface((390,198))
        textlayer = textlayer.convert_alpha()
        textlayer.fill((0,0,0,0))
        Rect = (self.WINDOWWIDTH/2.0-195, self.WINDOWHEIGHT-50)
        bgimage = pygame.image.load(self.textbgfile)
        textlayer.blit(bgimage,(0,0))
        text = font.render(self.textinput, 1, (0, 0, 0))
        if text.get_width()>325:
            self.textinput=self.textinput[:-1]
            self.blittextinput()
        else:
            textlayer.blit(text,(35,25))
            self.windowSurface.blit(textlayer,Rect)

    def getplayer(self,path,northimage,eastimage,southimage,westimage):
        print self,path,northimage,eastimage,southimage,westimage
        self.player = player(self,path,northimage,eastimage,southimage,westimage)

    def waitforkey(self,FPS):
        beenden=False
        downpressed=False
        uppressed=False
        speed = 0
        pygame.event.get()
        while not beenden:
            for event in pygame.event.get():
                if event.type == pgl.QUIT:
                    beenden=True
                if event.type in (pgl.KEYDOWN, pgl.KEYUP):
                    if event.key == pgl.K_PAGEUP:
                        uppressed = event.type == pgl.KEYDOWN
                    elif event.key == pgl.K_PAGEDOWN:
                        downpressed = event.type == pgl.KEYDOWN
                    elif event.type == pgl.KEYDOWN:
                        beenden = True
            speed=speed*0.9
            if uppressed:
                speed-=0.1
            elif downpressed:
                speed+=0.1
            self.textpointer+=speed
            self.mainClock.tick(FPS)
            self.update()

    def loop(self,onlyone=False,swapdirkeys=True):
        dirkeys=[pgl.K_UP,pgl.K_RIGHT,pgl.K_DOWN,pgl.K_LEFT]
        pygame.mouse.set_visible(False)
        beenden=False
        # check for events
        events=pygame.event.get()
        if onlyone and len(events):
            events=[events[0]]
            #print "tick"
        for event in events:
            if event.type == pgl.QUIT:
                beenden=True
            if event.type == pgl.KEYDOWN:
                key=event.key
                if event.key in dirkeys and swapdirkeys:
                    key=dirkeys[(dirkeys.index(event.key)+{"oben":0,"rechts":1,"unten":2,"links":3}[self.blickrichtung])%4]
                if key == pgl.K_LCTRL:
                    self._strg=True
                elif self._strg:
                    self._keylist.append(key)
                elif key in self._keydown_bindings.keys() or\
                     event.unicode in self._keydown_bindings.keys():
                    if event.unicode and event.unicode in printable:
                        self._keydown_bindings[event.unicode]()
                    else:
                        self._keydown_bindings[key]()
                    
            if event.type == pgl.KEYUP:
                key=event.key
                if event.key in dirkeys and swapdirkeys:
                    key = dirkeys[(dirkeys.index(event.key)+{"oben":0,"rechts":1,"unten":2,"links":3}[self.blickrichtung])%4]
                if key == pgl.K_LCTRL:
                    self._strg=False
                    if tuple(self._keylist) in self._keylist_bindings.keys():
                        self._keylist_bindings[tuple(self._keylist)]()
                    self._keylist=[]
                elif self._strg:
                    pass
                elif key in self._keyup_bindings.keys():
                    self._keyup_bindings[key]()
                    
            if event.type == pgl.MOUSEBUTTONDOWN:
                if self._mousedown_bindings.has_key(event.button):
                    self._mousedown_bindings[event.button](event.pos)

            if event.type == pgl.MOUSEBUTTONUP:
                pass

            if event.type == pgl.MOUSEMOTION:
                self.mousepos = event.pos
        return not beenden


if __name__ == "__main__":
    verzeichnis1 = "/home/joram/Shildiwelt1.8/data/Objekte/"
    verzeichnis2= "../data/Objekte/"

    pygame.init()
    screen=pygame.display.set_mode((800,480))
                                   #,pygame.FULLSCREEN)
    landi = pygame_landschaft(verzeichnis2,
                              width=800,
                              height=480,screenobject=screen)
    landi.landschaft(
#        "../data/Landschaften/testpnglandschaft.shl",)
         "../data/Landschaften/garten.shl",)
#        "../data/Landschaften/kanalisation.shl",)
#        "../data/Landschaften/wald.shl",)
#        "../data/Landschaften/schuppen.shl",)
#        "../data/Landschaften/fachwerktest.shl",)
#        "../data/Landschaften/3dtest.shl",)
    


    landi.speed(10)
    #print landi.kaestcheneigenschaften
    landi.move(100,-100)
    
    #landi.getplayer(verzeichnis1,
    #                "Trainer/Charlie.gif",
    #                "Trainer/Charlie.gif",
    #                "Trainer/Charlie.gif",
    #                "Trainer/Charlie.gif")
    
    FPS=16
    x=0
    import math, time
    tlistlist=[]
    #landi.move(-150,0)
    while landi.loop():
        x+=0.2
        landi.goto(math.sin(x)*50+50,math.cos(x)*50)
        #landi.move(math.sin(x)*22,0)
        #landi.light=int((math.sin(x/5)+1)*128)
        #if int(x)%2:
        #    landi.move(-50,0)
        #else:
        #    landi.move(50,0)
        t = time.time()
        tlist=landi.update()
        tlist.append(time.time()-t)
        tlist.append(1/(time.time()-t))
        tlistlist.append(tlist)
        #landi.mainClock.tick(FPS)
        #print landi.tellpos()
    landi.text(
        u"""Herzlich willkommen.
Shildimon ist ein freies Adventure- / Strategiespiel,
bei welchem man die Rolle eines Charakters übernimmt,
Landschaften erforscht und Rätsel löst./nEs spielt auf dem fiktiven Planeten Teku.
Shildimon ist ein freies und in Python verfasstes Programm,
welches sich momentan noch in der Entstehungsphase befindet.
"""
        )

    for i in range(len(tlistlist[0])):
        print sum([tlist[i]/len(tlistlist) for tlist in tlistlist]),
    landi.textinput="Hallo Welt! 123456789123456789123456789"
    landi.text(u"tschüss")
    print landi.auswahl(["ja","nein","vielleicht","1","2","3","4","5","6"])
    landi.quit()
