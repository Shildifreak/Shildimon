#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2008 Günter Milde.
#             Released  without warranties or conditions of any kind
#             under the terms of the Apache License, Version 2.0
# 	      http://www.apache.org/licenses/LICENSE-2.0
# :Id: $Id:  $

# shildi-klassen.py: 
# ============================================================

# Wie mache ich mir einen Datencontainer aus einer Klasse?

class Tile(object):
    """Landschafts-Kästchen"""
    xy = (0,0)
    bild = None
    action = None
    bg = "black"
    
    def __init__(self,**kwargs):
        """alle Keyword-Argumente als Instanz-Argumente eintragen"""
        self.__dict__.update(kwargs)
        
    def __repr__(self):
        return "Tile(xy=%s, bild=%s, action=%s, bg=%s)" % (
                     self.xy, self.bild, self.action, self.bg)
    
    def __str__(self):
        return "{xy: %s, bild: %s, action: %s, bg: %s}" % (
                     self.xy, self.bild, self.action, self.bg)
        

# Wie verwende ich so was?

bsp = Tile(bild='bsp.png', xy=(1,3))

# einfaches ansprechen der Elemente
print bsp.xy, bsp.bild, bsp.action, bsp.bg

# String-Repräsentation gut zu lesen
print str(bsp)

# eval(repr(bsp)) == bsp
print repr(bsp)

# eine Landschaft als Dictionary von Kästchen
Landschaft = {}

for kaestchen in [bsp]:
    Landschaft[kaestchen.xy] = kaestchen
    
print Landschaft    


# Eine Konfigurationsdatei im Python Standard Format lesen

import ConfigParser, os

configleser = ConfigParser.ConfigParser()

# start-vorgabewerte für neue spieler
# muß existieren!
# config.readfp(open('defaults.cfg'))

# [DEFAULT]
# name: neuer Spieler
# landschaft: 'Heimatstadt.cfg'
# punkte: 0
# shildinge: 100  # Geld
# eine liste: 1, 3, 6, 45

# aktuelle Konfiguration eines Spielers
gelesen = configleser.read(os.path.expanduser('~/.shildimon.cfg'))

print "Konfigurationsdateien",gelesen,"gelesen."

print configleser.defaults()

# ein anderer Parser für die Landschaftsdaten
landschaft = ConfigParser.ConfigParser()

# das wird vom Programm geändert
aktuelle_landschaft = 'bsp.cfg'

landschaft.read(aktuelle_landschaft)


