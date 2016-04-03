#!/usr/share/python
# -*- coding: utf8 -*-

#  2007-2014 Joram Brenz
# File:  Mainwalk of MCGEM
# Autor: Joram Brenz
# License: GPLv3

tmp_timesum = 0
tmp_istiming = False
tmp_counter = 0

RETURNVALUE=None

print("mainwalk.py started")

# IMPORTANWEISUNGEN
import sys
import os.path
sys.path.insert(1,sys.path[0]+os.path.sep+"modules")#+os.path.sep)
#sys.path.insert(1,"modules")
#print sys.path
#print("added path: " + sys.path[2])
import ConfigParser
from ast import literal_eval
import time
from string import printable
printable=unicode(printable.replace("\n","").replace("\r","").replace("\t",""))+u"ÄÖÜäöüß"

from pygame_menuerstellen import openmenu
from Laufzeitaufrufer import Laufzeitaufrufer
import pygame
import pygame.locals as pgl
import pygame_landschaft
from itemfuncs import itemmenu, itemsurface, getdefaults
#help(pygame_landschaft)

reload(pygame_landschaft)

# VERZEICHNISSE #
sep = os.path.sep
shildiverzeichnis = sys.path[0]+sep
#shildiverzeichnis = "."+sep
Sounddir    = shildiverzeichnis+"data%sSounds%s" %(sep,sep)
Musicdir    = shildiverzeichnis+"data%sMusik%s" %(sep,sep)
Defaultfile = shildiverzeichnis+"data%sgrundeinstellungen.cfg" %sep
Configfile  = os.path.expanduser("~"+sep+".mcgame.cfg")
Tilesdir    = shildiverzeichnis+"data%sObjekte%s" %(sep,sep)
Sceneryfile = shildiverzeichnis+"data%sLandschaften%s" %(sep,sep)
Otherdir    = shildiverzeichnis+"data%sother%s" %(sep,sep)
Itemdir     = shildiverzeichnis+"data%sObjekte%sItems%s" %(sep,sep,sep)
Imagedir    = shildiverzeichnis+"data%sObjekte%sImages%s" %(sep,sep,sep)
Personsdir  = shildiverzeichnis+"data%sObjekte%sPersonen%s" %(sep,sep,sep)
Crodedir    = shildiverzeichnis+"data%sCrode%s" %(sep,sep)

MAX_FPS = 100
LEFTHAND  = (15,12)
RIGHTHAND = (23,12)

# DATEIEN #
#bgmusictitle="by_joram"+sep+"sstandartm.mid"
bgmusictitle="lizard.mod"

#print shildiverzeichnis

volume = 0.5
# MUSIK
pygame.mixer.init()
aua = pygame.mixer.Sound(Sounddir+"hurt.wav")
aua.set_volume(volume)
backgroundmusic=pygame.mixer.music
backgroundmusic.load(Musicdir+bgmusictitle)
#backgroundmusic.play(-1)
backgroundmusic.set_volume(volume)
print "Musikplayer initialisiert"

def setvolume(newvolume):
    global volume, spieler
    spieler.daten["volume"]=newvolume
    volume = newvolume
    aua.set_volume(volume);backgroundmusic.set_volume(volume)


# SPIELER

richtung="oben"
class varstore():
    pass
spieler = varstore() 
# aktuelle Konfiguration eines Spielers laden
def configure_player():
    global spieler, configleser
    configleser = ConfigParser.ConfigParser()
    #print Configfile
    configleser.read(Configfile)
    if configleser.defaults() == {}:#noch kein spielerconfigfile existiert
        configleser.read(Defaultfile)
        spieler.daten=dict(configleser.items("EINSTELLUNGEN"))
        #spieler.daten["name"]=askstring("Name","Wie heißt du?")
        spieler.daten["name"]="Marie"
        spieler.var = {"None":"None"}
        spieler.items=literal_eval(dict(configleser.items("ITEMS"))["items"])
    else:
        spieler.daten=dict(configleser.items("EINSTELLUNGEN"))
        spieler.var  =dict(configleser.items("VARIABLEN"))
        spieler.items=dict(configleser.items("ITEMS"))
        spieler.items=literal_eval(dict(configleser.items("ITEMS"))["items"])
    landi.getplayer(Personsdir,
                    spieler.daten["shape"]+"_back.gif",
                    spieler.daten["shape"]+"_right.gif",
                    spieler.daten["shape"]+"_front.gif",
                    spieler.daten["shape"]+"_left.gif")
    landi.playerlight=(int(spieler.daten["light"].split(",")[0]),
                       int(spieler.daten["light"].split(",")[1]))
    landi.player.setitems(spieler.items,Itemdir)
    
# LANDSCHAFTSFUNKTIONEN

landschaft = "Testlandschaft"
reaktionslaufen = lambda: "dummyfunktion"

def landschaftneueinrichten(wo = (0,0)):
    global kaestcheneigenschaften , landschaft, richtung, landi, bgmusictitle
    #print Sceneryfile+landschaft+".shl"
    try:
        open(Sceneryfile+landschaft+".shl")
        landi.landschaft(Sceneryfile+landschaft+".shl")
    except:
        print("Fehler beim Laden von: "+Sceneryfile+landschaft+".shl")
    else:
        spieler.daten["landschaft"]=landschaft
        print("Erfolgreiches Laden von: "+Sceneryfile+landschaft+".shl")#landi.kaestcheneigenschaften
        try:
            if bgmusictitle!=landi.eigenschaften["music"]:
                bgmusictitle=landi.eigenschaften["music"]
                bgmusictitle=bgmusictitle.replace("/",sep)    
                backgroundmusic.load(Musicdir+bgmusictitle)
                backgroundmusic.play(-1)
                print("Hintergrundmusik %s erfolgreich gestartet") %bgmusictitle
            else:
                print("Hintergrundmusik %s bleibt") %bgmusictitle
        except:
            print("konnte Hintergrungmusik %s nicht laden") %(Musicdir+bgmusictitle)


        landi.goto(wo[0]*50,wo[1]*50)
        spieler.daten["richtung"] = "oben" #M#
        landi.update(itemsurface(spieler.items,Itemdir),
                     objactfunc=reaktionslaufen,force_update=True)
        if landi.eigenschaften.has_key("initaction"):
            richtung="init"
            reaktionslaufen(landi.eigenschaften["initaction"])
        else:
            print "no initaction found"
        

#Variablen für laufen:
ende = False
richtung = False
richtungoben = False
richtungrechts = False
richtunglinks = False
richtungunten = False

# -------------------------andere Funktionen----------------------------#
def feld_pos(ort=None):
    if ort is None:
        ort = landi.tellpos()
    return (int(round(ort[0]/50)), int(round(ort[1]/50)))

def neuelandschaft():
    global landschaft
    textinput=landi.textinput
    landi.textinput=""
    if textinput != "":
        landschaft = textinput
        landschaftneueinrichten()

def schummeln():
    #try:
    textinput=landi.textinput
    landi.textinput=""
    reaktionslaufen(textinput)
    #except:
    #    print "Fehler beim auswerten von Schummelbefehl."

def beenden():
    global ende
    ende = True

def gib(erzaehlung):
    print erzaehlung


def find(string,gesucht):
	for i in range (len(string)):
		string2 = string[i:]
		if string2.startswith(gesucht):
			return i

splitcache = {}

def splitmitklammern(string,trennzeichen=","):
    if not splitcache.has_key((string,trennzeichen)):
        splitcache[(string,trennzeichen)] = splitmitklammern2(string, trennzeichen)
    return splitcache[(string,trennzeichen)]

def splitmitklammern3(string,trennzeichen=","):
    if set(trennzeichen).isdisjoint(set(string)):
        return [string]
    j=0
    i=0
    anzklammern = 0
    while i<len(string):
        pass
        

def splitmitklammern2(string,trennzeichen=","):
    if set(trennzeichen).isdisjoint(set(string)):
        return [string]
    b = []; anzoklamm = 0; letzteskomma = 0; isstring = False
    for i in range(len(string)):
        if string[i]=="\"":
            isstring = not isstring
        if not isstring:
            if string[i] in "([{":
                anzoklamm += 1
            elif string[i] in ")]}":
                anzoklamm -= 1
            elif not anzoklamm > 0:
                if string[i] in trennzeichen:
                    b.append(string[letzteskomma:i])
                    letzteskomma = i+1
    b.append(string[letzteskomma:])
    return b

def textschreiben(text):
    if type(text)==str:
        text=text.decode("utf8")
    readspeed=float(spieler.daten["lesegeschwindigkeit"])
    landi.text(text,readspeed,MAX_FPS)

def addtextinput(buchstabe):
    landi.textinput+=buchstabe

def deltextinput():
    landi.textinput=landi.textinput[:-1]

def setblickrichtung(richtung):
    landi.blickrichtung=richtung
    spieler.daten["blickrichtung"]=richtung

# -----------------------------das menu---------------------------------#
def itemmenuaufrufen(FULLSCREEN):
    if richtung:
        return
    #print("open Itemmenu")
    #print(spieler.items)
    putofallrichtungen()
    pages = [[["Player0",spieler.items],(0,0)]]
    pages = itemmenu(pages,Itemdir,FULLSCREEN)
    spieler.items = pages[0][0][1]
    landi.player.setitems(spieler.items,Itemdir)
    landi.update(force_update=True)

def setwritespeed(speed):
    global spieler
    spieler.daten["lesegeschwindigkeit"]=speed

def skiptoend():
    global landschaft
    landschaft="labordonovan"
    landschaftneueinrichten((0,3))

def itemmenulistenerstellen(FULLSCREEN):
    global menuliste
    volumelist= [("aus",       lambda:setvolume(0.00)),
                 ("sehr leise",lambda:setvolume(0.01)),
                 ("leise",     lambda:setvolume(0.10)),
                 ("mittel",    lambda:setvolume(0.5)),
                 ("laut" ,     lambda:setvolume(1.00)),
                 ("sehr laut", lambda:setvolume(2.00)),
                 (u"zurück","back"),
                 ]
    textanilist=[("aus",       lambda:setwritespeed(0)),
                 ("an",        lambda:setwritespeed(1)),
                 ("extra slow",lambda:setwritespeed(2)),
                 (u"zurück","back"),
                 ]
    einstellungsliste = [
                 (u"Lautstärke",volumelist),
                 ("Textanimation",textanilist),
                 (u"zurück","back"),
                 ]
    sonstiges = [
                 ("Zum Ende des Spiels springen",[
                     (u"Ja ich möchte zum Ende des Spiels springen",skiptoend),
                     ("Nein lieber doch nicht","back")
                     ]),
                 (u"zurück","back"),
                 ]
    menuliste = [("Items",lambda:itemmenuaufrufen(FULLSCREEN)),
                 ("Einstellungen",einstellungsliste),
                 ("Sonstiges",sonstiges),
                 #("erinnern",lambda :textli.reinorausfahren(True)),
                 ("Beenden",beenden),
                 (u"zurück","quit"),
                 ]

def defopenshildimenu(screen,FULLSCREEN):
    global openshildimenu
    itemmenulistenerstellen(FULLSCREEN)
    def openshildimenu():
        if richtung:
            return
        putofallrichtungen()
        openmenu(menuliste,screen=screen,FULLSCREEN=FULLSCREEN,
                 inform="error",title="MCGEM")
        landi.update(force_update=True)
# ----------------------------immerwieder-------------------------------#

immerwieder = Laufzeitaufrufer()
#immerwieder.putin(befehl,time_in_seconds)

# ---------------- jetzt das was man zum laufen braucht ----------------#

def gehzurichtung(wohin):
    global landschaft #M# , spieler, landi

    x,y = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
           }.get(wohin,(0,0))
        
    zielfeld = (feld_pos()[0]+x,feld_pos()[1]+y)
    objektaction=False
    for pos in landi.cobjektsbypos.keys():
        if pos == zielfeld:
            objekt=landi.cobjektsbypos[pos]
            if objekt.data["action"]!="None" and objekt.data["action"]!="":
                objektaction=objekt.data["action"]
    if spieler.daten["richtung"] != wohin :
        if wohin == "oben":
            landi.player.looksouth()
        if wohin == "rechts":
            landi.player.lookwest()
        if wohin == "unten":
            landi.player.looknorth()
        if wohin == "links":
            landi.player.lookeast()
        spieler.daten["richtung"]=wohin
    elif objektaction:
        reaktionslaufen(objektaction)
    elif zielfeld in landi.kaestcheneigenschaften.keys():
        reaktionslaufen(landi.kaestcheneigenschaften[zielfeld])

    landi.goto(feld_pos()[0]*50,feld_pos()[1]*50)
    spieler.daten["x-position"]=repr(int(landi.tellpos()[0]/50.0))
    spieler.daten["y-position"]=repr(int(landi.tellpos()[1]/50.0))


def reaktionslaufen(wasishier):
    global landschaft, stehaction, stehort, stehbeginnzeit, RETURNVALUE, ende, tmp_timesum,tmp_istiming,tmp_counter #M#, spieler, landi
    if tmp_istiming:
        return reaktionslaufen2(wasishier)
    else:
        tmp_istiming = True
        tmp_counter+=1
        tmp_time2 = time.time()
        ret = reaktionslaufen2(wasishier)
        tmp_timesum += time.time()-tmp_time2
        tmp_istiming = False
        return ret

def reaktionslaufen2(wasishier):
    global landschaft, stehaction, stehort, stehbeginnzeit, RETURNVALUE, ende #M#, spieler, landi

    x,y = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
           }.get(spieler.daten["richtung"],(0,0))

    if wasishier.startswith("\"") and wasishier.endswith("\""):
        return wasishier
    if wasishier in ("None","none","nichts"):
        return wasishier

    if len(splitmitklammern(wasishier,"=+"))!=1:
        if len(splitmitklammern(wasishier,"="))>1:
            aussagen=splitmitklammern(wasishier,"=")
            aussagen=[reaktionslaufen(i).lower().replace('"',"") for i in aussagen]
            return str(aussagen[0]==aussagen[1]).lower()
    elif "(" in wasishier:
        befehl=wasishier[:wasishier.find("(")]
        argumente=splitmitklammern(wasishier[wasishier.find("(")+1:-1])
    else:
        befehl=wasishier
        argumente=[]

    # DIE IN DEM FELD VERZEICHNETE AKTION AUSFÜHREN

    # schauen ob das Feld object.action() enstpricht -> objectaction
    if "." in befehl and argumente!=[]:
        if befehl[:befehl.find(".")]=="player":
            return landi.player.reaktionslaufen(wasishier[wasishier.find(".")+1:])
        else:
            return landi.complexobjekts[wasishier[:wasishier.find(".")]
            ].reaktionslaufen(wasishier[wasishier.find(".")+1:])

    # >>> programm.cfg
    elif befehl.endswith(".cfg"):
        if not landi.crodespeicher.has_key(befehl):
            crodefile=open(Crodedir+befehl,"r")
            landi.crodespeicher[befehl]=crodefile.read().replace("\n","")
        return reaktionslaufen(landi.crodespeicher[befehl])        

    # >>> ()
    elif befehl=="":
        argumente=[reaktionslaufen(i) for i in argumente]
        return "none"

    # >>> wenn(wert1=wert2,dann[,sonst])
    elif befehl == "wenn":
        argumente[0]=reaktionslaufen(argumente[0])
        if argumente[0]=="true":
            return reaktionslaufen(argumente[1])
        elif len(splitmitklammern(wasishier[5:-1]))>=3:
            return reaktionslaufen(argumente[2])
        return "none"

    # >>> case(wert,wert1,dann,wert2,dann,wert3,dann[,sonst])
    elif befehl == "case":
        argumente[0]=reaktionslaufen(argumente[0])
        for i in range((len(argumente)-1)/2):
            if argumente[0] == argumente[i*2+1]:
                return reaktionslaufen(argumente[i*2+2])

    # add(z1,z2)
    elif befehl=="add":
        argumente=[reaktionslaufen(i) for i in argumente]
        return str(int(argumente[0])+int(argumente[1]))

    # sub(z1,z2)
    elif befehl=="sub":
        argumente=[reaktionslaufen(i) for i in argumente]
        return str(int(argumente[0])-int(argumente[1]))

    # mul(z1,z2)
    elif befehl=="mul":
        argumente=[reaktionslaufen(i) for i in argumente]
        return str(int(argumente[0])*int(argumente[1]))

    # div(z1,z2)
    elif befehl=="div":
        argumente=[reaktionslaufen(i) for i in argumente]
        return str(int(argumente[0])/int(argumente[1]))

    # mod(z1,z2)
    elif befehl=="mod":
        argumente=[reaktionslaufen(i) for i in argumente]
        return str(int(argumente[0])%int(argumente[1]))

    # >>> time(faktor)
    elif befehl == "time":
        if argumente:
            argumente=[reaktionslaufen(i) for i in argumente]
            faktor = int(argumente[0])
        else:
            faktor = 1
        return str(int(time.time()*faktor))

    # >>> .
    elif befehl == ".":
        landi.move(x*50,y*50,MAX_FPS,spieler.daten["geschwindigkeit"])
        return "none"
    
    # >>> x
    elif befehl == "x":
        aua.play()
        return "none"

    # >>> xrltb
    elif befehl.startswith("x") and (
         "r" in befehl or "l" in befehl or
         "t" in befehl or "b" in befehl):
        #print landi.heading()
        if (landi.player.direction=="south" and "t" not in befehl) or (
            landi.player.direction=="west"  and "r" not in befehl) or (
            landi.player.direction=="north" and "b" not in befehl) or (
            landi.player.direction=="east"  and "l" not in befehl):
            landi.move(x*50,y*50,MAX_FPS,spieler.daten["geschwindigkeit"])
        return "none"

    # >>> dreheoben
    elif befehl == "dreheoben":
        landi.player.looksouth()
        spieler.daten["richtung"] = "oben"
        return "none"

    # >>> dreherechts
    elif befehl == "dreherechts":
        landi.player.lookwest()
        spieler.daten["richtung"] = "rechts"
        return "none"

    # >>> dreheunten
    elif befehl == "dreheunten":
        landi.player.looknorth()
        spieler.daten["richtung"] = "unten"
        return "none"

    # >>> drehelinks
    elif befehl == "drehelinks":
        landi.player.lookeast()
        spieler.daten["richtung"] = "links"
        return "none"

    # >>> oben oder unten oder links oder rechts
    elif befehl in ("oben","unten","links","rechts"):
        gehzurichtung(befehl)
        return "none"

    elif befehl in ("voben","vunten","vlinks","vrechts"):
        setblickrichtung(befehl[1:])

    # >>> < oder v oder ^ oder >
    elif befehl in ("v","^","<",">"):
        landi.move(x*50,y*50,MAX_FPS,spieler.daten["geschwindigkeit"])
        if befehl == "v":
            reaktionslaufen("dreheunten")
        elif befehl == "<":
            reaktionslaufen("drehelinks")
        elif befehl == "^":
            reaktionslaufen("dreheoben")
        elif befehl == ">":
            reaktionslaufen("dreherechts")
        x,y = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
               }.get(spieler.daten["richtung"],(0,0))
        landi.move(x*50,y*50,MAX_FPS,spieler.daten["geschwindigkeit"])
        return "none"

    # >>> open(landschaft,x,y)
    elif befehl == "open":
        argumente=[reaktionslaufen(i) for i in argumente]
        landschaft = argumente[0]
        wo = [int(i) for i in argumente[1:3]]   #genauso wie: (int(wo[0],wo[1]))
        if wo:
        #print landschaft, wo
            landschaftneueinrichten(wo)
        else:
            landschaftneueinrichten()
        return "none"

    # >>> goto(x,y)
    elif befehl == "goto":
        argumente=[reaktionslaufen(i) for i in argumente]
        wo = [int(i)*50 for i in argumente[0:2]]
        landi.goto(wo[0],wo[1])
        return "none"

    # >>> text(text)
    elif befehl == "text":
        argumente=[reaktionslaufen(i) for i in argumente]
        putofobenvariable()
        putofrechtsvariable()
        putofuntenvariable()
        putoflinksvariable()
        #print "ich sage dir:",wasishier
        for text in argumente:
            if text.startswith("\""):
                text=text[1:]
            if text.endswith("\""):
                text=text[:-1]
            textschreiben(text)
        return "none"

    # >>> var(varname=wert)
    elif befehl == "var":
        argumente=[reaktionslaufen(i) for i in argumente]
        variable = argumente[0]
        if "." not in variable:
            longvariable = landschaft+"."+variable
        else:
            longvariable = variable
        if spieler.var.has_key(longvariable):
            return spieler.var[longvariable]
        elif spieler.daten.has_key(variable):
            return spieler.daten[variable]
        else:
            return "none"

    # >>> varset(varname=wert[,varname2=wert2,...])
    elif befehl == "varset":
        for argument in argumente:
            variable, wert = [reaktionslaufen(i) for i in argument.split("=")]
            if "." not in variable:
                variable = landschaft+"."+variable
            spieler.var[variable]=wert
        return "none"

    # >>> setlight(wert)
    elif befehl == "setlight":
        argumente=[reaktionslaufen(i) for i in argumente]
        landi.light = int(argumente[0])
        return "none"

    # >>> setplayerlight(radius,level)
    elif befehl == "setplayerlight":
        argumente=[reaktionslaufen(i) for i in argumente]
        spieler.daten["light"] = (int(argumente[0]),
                                  int(argumente[1]))
        landi.playerlight = spieler.daten["light"]
        return "none"

    # >>> e / eis / ice
    elif befehl in ("e","eis","ice") and x!=0 and y!=0:
        landi.move(x*50,y*50,MAX_FPS,spieler.daten["geschwindigkeit"])
        gehzurichtung(richtung)
        return "none"

    # >>> timer(Sekunden,Befehl)
    elif befehl=="timer":
        delay,action = argumente[0:2]
        delay=reaktionslaufen(delay)
        stehbeginnzeit=time.time()
        stehaction = (delay,action)
        stehort = landi.pos
        #print stehaction
        return "none"
    
    # >>> sound(Dateiname)
    elif befehl=="sound":
        argumente=[reaktionslaufen(i) for i in argumente]
        soundfilename = argumente[0]
        #print("played Sound: "+soundfilename)
        gamesound = pygame.mixer.Sound(Sounddir+soundfilename)
        gamesound.set_volume(volume)
        gamesound.play()
        return "none"

    # >>> image(Dateiname)
    elif befehl=="image":
        argumente=[reaktionslaufen(i) for i in argumente]
        imagefilename = argumente[0]
        #print("displayed Image: "Imagedir+imagefilename)
        putofallrichtungen()
        landi.showimage(Imagedir+imagefilename)
        landi.update(force_update=True)
        return "none"

    # >>> getitem(itemname,wenngeschafft,sonst)
    elif befehl=="getitem":
        argumente[0]=reaktionslaufen(argumente[0])
        aufgenommen=False
        if not spieler.items.has_key(RIGHTHAND):
            spieler.items[RIGHTHAND]=[argumente[0]+"0",{}]
            aufgenommen=True
        elif not spieler.items.has_key(LEFTHAND):
            spieler.items[LEFTHAND]=[argumente[0]+"0",{}]
            aufgenommen=True
        if aufgenommen==True and len(argumente)>=2:
            reaktionslaufen(argumente[1])
        elif len(argumente)>=3:
            reaktionslaufen(argumente[2])
        landi.player.setitems(spieler.items,Itemdir)    
        return str(aufgenommen).lower()

    # >>> removeitem(itemname,wenngeschafft,sonst)
    elif befehl=="removeitem":
        argumente[0]=reaktionslaufen(argumente[0])
        if "@" in argumente[0]:
            variable, argumente[0] = argumente[0].split("@")
            if not "." in variable:
                variable=landschaft+"."+variable
            inventar = literal_eval(spieler.var[variable])
        else:
            variable = None
            inventar = spieler.items
        def removeitem(inventar):
            abgelegt=False
            for key in inventar.keys():
                if inventar[key][1] != {}:
                    inventar[key][1],abgelegt=removeitem(inventar[key][1])
                elif inventar[key][0][:-1]==argumente[0]:
                    inventar.pop(key)
                    abgelegt=True
                if abgelegt:
                    return inventar, abgelegt
            return inventar, abgelegt
        inventar,abgelegt=removeitem(inventar)
        if variable:
            spieler.var[variable]=str(inventar)
        else:
            spieler.items=inventar
        if abgelegt==True and len(argumente)>=2:
            reaktionslaufen(argumente[1])
        elif len(argumente)>=3:
            reaktionslaufen(argumente[2])
        landi.player.setitems(spieler.items,Itemdir)
        return str(abgelegt).lower()

    # >>> wennitem(itemname,dann,sonst)
    elif befehl=="wennitem":
        argumente[0]=reaktionslaufen(argumente[0])
        if "@" in argumente[0]:
            argumente[0], variable = argumente[0].split("@")
            if not "." in variable:
                variable=landschaft+"."+variable
            inventar = literal_eval(spieler.var[variable])
        else:
            variable = None
            inventar = spieler.items
        def testforitem(inventar):
            itemda=False
            for key in inventar.keys():
                if inventar[key][1] != {}:
                    itemda=testforitem(inventar[key][1])
                elif inventar[key][0][:-1]==argumente[0]:
                    itemda=True
                if itemda:
                    return itemda
            return itemda
        itemda=testforitem(inventar)
        if itemda==True and len(argumente)>=2:
            reaktionslaufen(argumente[1])
        elif len(argumente)>=3:
            reaktionslaufen(argumente[2])
        return "none" #M# ersetzen der Funktion durch hasitem

    elif befehl=="wearsitem":
        return "none"

    # >>> truhe(variable,item,{standartinhalt})
    elif befehl=="truhe":
        variable,item,standartinhalt=argumente[0:3]
        variable=reaktionslaufen(variable)
        item=reaktionslaufen(item)
        if not "." in variable:
            variable=landschaft+"."+variable
        putofallrichtungen()
        if spieler.var.get(variable,"none").lower()=="none":
            spieler.var[variable]=standartinhalt
        inhalt=literal_eval(spieler.var[variable])

        print inhalt
        pages = [[["Player0",spieler.items],(0,0)],
                 [[item+"0",inhalt],(0,-480)]]
        pages = itemmenu(pages,Itemdir,landi.FULLSCREEN)
        spieler.items = pages[0][0][1]
        spieler.var[variable]=str(pages[1][0][1])
        landi.player.setitems(spieler.items,Itemdir)
        landi.update(force_update=True)
        return "none"

    # >>> push(objekt)
    elif befehl=="push":
        argumente=[reaktionslaufen(i) for i in argumente]

        xpos = landi.complexobjekts[argumente[0]].xpos
        ypos = landi.complexobjekts[argumente[0]].ypos
        x = ((xpos+25-landi.size[0]/2)*-1)/50
        y = ((ypos+25-landi.size[1]/2)/50)
        xd,yd = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
               }.get(spieler.daten["richtung"],(0,0))        
        zielfeld = (x+xd,y+yd)
        action=landi.kaestcheneigenschaften.get(zielfeld,"x")
        for pos in landi.cobjektsbypos.keys():
            if pos == zielfeld:
                objekt=landi.cobjektsbypos[pos]
                if objekt.data["action"]!="None" and objekt.data["action"]!="":
                    action=objekt.data["action"]
        if action in ("."):
            reaktionslaufen(argumente[0]+".move("+str(-xd)+","+str(yd)+")")
        return "none"

    # >>> objekton(x,y)
    elif befehl=="objekton":
        argumente=[reaktionslaufen(i) for i in argumente]
        print "Objekton:", (argumente[0],argumente[1]),landi.cobjektsbypos.keys()
        return str((int(argumente[0]),int(argumente[1])) in landi.cobjektsbypos.keys()).lower()
    
    # >>> update
    elif befehl=="update":
        landi.update(itemsurface(spieler.items,Itemdir),
                     objactfunc=reaktionslaufen)
        return "none"

    # >>> close(returnvalue)
    elif befehl=="close":
        argumente=[reaktionslaufen(i) for i in argumente]
        if len(argumente)>=0:
            RETURNVALUE=argumente[0]
        ende=True
        return "none"

    # >>> wenn befehl kein bekannter befehl ist nimm es als festen wert an:
    elif argumente==[]:
        return befehl

    else:
        print "Befehl",befehl,"was not found."
        return "error"

def putonobenvariable(*var):
    global richtungoben
    richtungoben = True
def putonrechtsvariable(*var):
    global richtungrechts
    richtungrechts = True
def putonuntenvariable(*var):
    global richtungunten
    richtungunten = True
def putonlinksvariable(*var):
    global richtunglinks
    richtunglinks = True

def putofobenvariable(*var):
    global richtungoben
    richtungoben = False
def putofrechtsvariable(*var):
    global richtungrechts
    richtungrechts = False
def putofuntenvariable(*var):
    global richtungunten
    richtungunten = False
def putoflinksvariable(*var):
    global richtunglinks
    richtunglinks = False
def putofallrichtungen():
    global richtungoben, richtungrechts, richtungunten, richtunglinks
    richtungoben,richtungrechts,richtungunten,richtunglinks=False,False,False,False

def usehand(hand):
    global landschaft, spieler, landi, richtung
    item = spieler.items.get(hand,"None")
    if richtung:
        return
    if item == "None":
        item = "Hand"
        itemname = "Hand"
    else:
        item = item[0][:-1]
        itemname = getdefaults(item,Itemdir).get("akkusativ",item)
    textschreiben("Spieler benutzt "+itemname+".")
    item = item.lower()
    x,y = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
           }.get(spieler.daten["richtung"],(0,0))
        
    zielfeld = (feld_pos()[0]+x,feld_pos()[1]+y)

    if landi.kaestchenitems.has_key(zielfeld):
        if landi.kaestchenitems[zielfeld].has_key(item):
            reaktionslaufen(landi.kaestchenitems[zielfeld][item])
    landi.goto(feld_pos()[0]*50,feld_pos()[1]*50)
    spieler.daten["x-position"]=repr(int(landi.tellpos()[0]/50.0))
    spieler.daten["y-position"]=repr(int(landi.tellpos()[1]/50.0))
    #print(spieler.daten["x-position"],spieler.daten["y-position"])

def usetextinput():
    textinput=landi.textinput
    landi.textinput=""
    # Irgendeine Aktion, abhängig von der Eingabe

    x,y = {"oben":(0,1),"rechts":(1,0),"unten":(0,-1),"links":(-1,0),
           }.get(spieler.daten["richtung"],(0,0))
    zielfeld = (feld_pos()[0]+x,feld_pos()[1]+y)
    
    if landi.kaestchenitems.has_key(zielfeld):
        if landi.kaestchenitems[zielfeld].has_key("inputaction"):
            try:
                reaktionslaufen(landi.kaestchenitems[zielfeld]["inputaction"].replace("INPUT","\""+textinput+"\""))
            except:
                pass
    landi.goto(feld_pos()[0]*50,feld_pos()[1]*50)
    spieler.daten["x-position"]=repr(int(landi.tellpos()[0]/50.0))
    spieler.daten["y-position"]=repr(int(landi.tellpos()[1]/50.0))

#-----------------------------Hauptfunktion-----------------------------#



def setup(screen=None,FULLSCREEN=False):
    global richtung, ende, richtungausschalten, landschaft, landi, stehaction, spieler

    landi = pygame_landschaft.pygame_landschaft(Tilesdir,width=800,
                                                height=480,
                                                screenobject=screen,
                                                fullscreen=FULLSCREEN)
    configure_player()
    setblickrichtung(spieler.daten["blickrichtung"])
    defopenshildimenu(screen,FULLSCREEN)
    
    volume=float(spieler.daten["volume"])
    aua.set_volume(volume);backgroundmusic.set_volume(volume)
    backgroundmusic.play(-1)

    landschaft=spieler.daten["landschaft"]
    
    landi.onkey(putonobenvariable,   pgl.K_DOWN)
    landi.onkey(putonrechtsvariable, pgl.K_LEFT)
    landi.onkey(putonuntenvariable,  pgl.K_UP)
    landi.onkey(putonlinksvariable,  pgl.K_RIGHT)
    landi.onkeyrelease(putofobenvariable, pgl.K_DOWN)
    landi.onkeyrelease(putofrechtsvariable, pgl.K_LEFT)
    landi.onkeyrelease(putofuntenvariable, pgl.K_UP)
    landi.onkeyrelease(putoflinksvariable, pgl.K_RIGHT)
    landi.onkey(lambda:itemmenuaufrufen(FULLSCREEN),pgl.K_TAB)
    landi.onclick(lambda dummi:itemmenuaufrufen(FULLSCREEN),4)
    landi.onkeylist(schummeln,["c","h","e","a","t"])
    landi.onkeylist(neuelandschaft,["o","l"])
    landi.onkeyrelease(openshildimenu, pgl.K_ESCAPE)
    landi.onkeylist(lambda:usehand(LEFTHAND),["l"])#,pgl.K_SPACE])#[pgl.K_LEFT])
    landi.onkeylist(lambda:usehand(RIGHTHAND),["r"])#,pgl.K_SPACE])#[pgl.K_RIGHT])
    landi.onkeylist(lambda:usehand({"rechts":RIGHTHAND,"links":LEFTHAND
                    }[spieler.daten["haender"]]),[pgl.K_SPACE])
    landi.onkeylist(lambda:setblickrichtung("oben"),[pgl.K_UP])
    landi.onkeylist(lambda:setblickrichtung("rechts"),[pgl.K_RIGHT])
    landi.onkeylist(lambda:setblickrichtung("unten"),[pgl.K_DOWN])
    landi.onkeylist(lambda:setblickrichtung("links"),[pgl.K_LEFT])
    landi.onclick(lambda pos:usehand(LEFTHAND),{"rechts":3,"links":1}[spieler.daten["haender"]])
    landi.onclick(lambda pos:usehand(RIGHTHAND),{"rechts":1,"links":3}[spieler.daten["haender"]])
    
    for b in printable:
        landi.onkey(lambda b=b:addtextinput(b),b)
    landi.onkey(deltextinput,pgl.K_BACKSPACE)
    landi.onkey(usetextinput,pgl.K_RETURN)


def main(screen=None,FULLSCREEN=False,daten=None):
    global richtung, ende, letzterichtung, richtungausschalten,\
           landschaft, landi, stehaction, spieler,\
           stehort, stehbeginnzeit,\
           tmp_timesum, tmp_counter

    if daten:
        spieler.daten=daten
    x=   float(spieler.daten["x-position"])
    y=   float(spieler.daten["y-position"])
    landschaftneueinrichten((x,y))

    stehaction = (0,None)
    stehbeginnzeit = -1
    stehort = landi.pos
    print("starting main loop")
    counter = 0
    tmp_time1 = time.time()
    while not ende:
        #ZEITMESSUNG#
        if counter % 10 == 0:
            print tmp_timesum/(time.time()-tmp_time1),tmp_counter/10
            tmp_timesum = 0
            tmp_counter = 0
            tmp_time1=time.time()
        #-----------#
        counter += 1
        if richtung:
            gehzurichtung(richtung)
            if landi.pos!=stehort:
                stehbeginnzeit = time.time()
                stehaction=(0,None)
        elif time.time()-stehbeginnzeit >= float(stehaction[0]) and stehaction[1]!=None and stehbeginnzeit!=-1:
            #print "doing:",stehaction[1]
            reaktionslaufen(stehaction[1])
            stehaction=(0,None)

        # Richtung bestimmen:
        richtung = {
            (0,0,0,0):False,
            (0,0,0,1):"links" ,
            (0,0,1,0):"unten" ,
            (0,1,0,0):"rechts",
            (1,0,0,0):"oben"  ,
            (0,0,1,1):{0:"unten" ,1:"links" }[counter%4<2],
            (0,1,1,0):{0:"rechts",1:"unten" }[counter%4<2],
            (1,1,0,0):{0:"oben"  ,1:"rechts"}[counter%4<2],
            (1,0,0,1):{0:"links" ,1:"oben"  }[counter%4<2],
            (0,1,0,1):richtung,
            (1,0,1,0):richtung,
            (0,1,1,1):richtung,
            (1,1,1,0):richtung,
            (1,1,0,1):richtung,
            (1,0,1,1):richtung,
            (1,1,1,1):richtung,
            }[(richtungoben,richtungrechts,richtungunten,richtunglinks)]
            
        #if richtungoben:
        #    richtung="oben"
        #elif richtungunten:
        #    richtung="unten"
        #elif richtunglinks:
        #    richtung="links"
        #elif richtungrechts:
        #    richtung="rechts"
        #else:
        #    richtung = False
        #    richtungausschalten = False
            
        immerwieder.loop()
        landi.update(itemsurface(spieler.items,Itemdir),
                     objactfunc=reaktionslaufen)
        landi.mainClock.tick(MAX_FPS)
        if not landi.loop():
            ende=True

    ende = False #wichtig, falls main mehrmals gestartet wird



    # Speichern
    #print("saving player data")
    #configdatei=open(Configfile, 'wb')
    #for i in spieler.daten.items():
    #    configleser.set("EINSTELLUNGEN",i[0],i[1])
    #for i in spieler.var.items():
    #    configleser.set("VARIABLEN",i[0],i[1])
    #for i in spieler.items.items():
    #    configleser.set("ITEMS",i[0],i[1])
    #configleser.write(configdatei)
    #configdatei.close()

    # Zumachen
    if screen==None:
        backgroundmusic.fadeout(2000)
        landi.quit()
    print("mainwalk.py beended")
    #print spieler.var
    #print spieler.items
    #print spieler.daten
    return spieler.var,RETURNVALUE
    

if __name__ == "__main__":
    setup()
    main()
