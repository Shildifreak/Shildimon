#! /usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True # print debug messages, maybe raise instead of ignoring errors
RELOAD = False # reload modules to make sure newest version is used

import sys, os
import time
import hashlib

sys.path.append(os.path.join(os.path.abspath(os.path.curdir),"modules"))
if DEBUG:
    sys.argv.append("--debug")
if RELOAD:
    sys.argv.append("--reload")

import ast

import socket_connection
import client
import server

if "--reload" in sys.argv:
    reload(client)
    reload(server)
    reload(socket_connection)

curdir = os.path.abspath(os.path.curdir)
datadir = os.path.join(os.path.dirname(curdir),"data")
savedir = os.path.join(os.path.dirname(curdir),"saves")

gamesdir = os.path.join(datadir,"Spiele")
datadir = os.path.join(datadir,"commondata")
settingsfn = os.path.join(savedir,"settings.cfg")

print settingsfn

Display = client.Display(datadir,settingsfn)

def main_menu():
    while True:
        INPUT = Display.menu([("ShildiEngine2.0",1,(127,0,255)),
                              ("Singleplayer",),
                              ("Multiplayer",),
                              ("Quit",)
                              ])[0]
        if INPUT == 1:
            ret = singleplayer_menu()
            if ret != 0:
                break
        elif INPUT == 2:
            ret = multiplayer_menu()
            if ret != 0:
                break
        elif INPUT in (3,-1):
            break

                           ################
                           # Singleplayer #
                           ################

def singleplayer_menu():
    gamelist = ([("Select Game",1,(127,0,255))]+
                [(i,) for i in os.listdir(gamesdir)]+
                [("Back",)])
    while True:
        i_game = Display.menu(gamelist)[0]
        if i_game == -1:
            return -1
        if 0 < i_game < len(gamelist)-1:
            ret = game_menu(gamelist[i_game][0])
            if ret != 0:
                return ret-1
        if i_game == len(gamelist)-1:
            return 0

def game_menu(game):
    options = ([(game,1,(127,0,255)),
                ("Load Game",),
                ("New Game",),
                ("Back",)])
    while True:
        i_option = Display.menu(options)[0] #M# use game specific style here
        if i_option == -1:
            return -1
        if i_option == 1:
            ret = save_selection_menu(game)
            if ret != 0:
                return ret-1
        if i_option == 2:
            ret = create_save_menu(game)
            if ret != 0:
                return ret-1
        if i_option == 3:
            return 0

def save_selection_menu(game):
    savelist = ([("Select Save",1,(127,0,255))]+
                [(i.split(".")[0],) for i in os.listdir(os.path.join(savedir,game))]+
                [("Back",)])
    while True:
        i_save = Display.menu(savelist)[0]
        if i_save == -1:
            return -1
        if 0 < i_save < len(savelist)-1:
            save = savelist[i_save][0]+".cfg"
            ret = singleplayer(game,save)
            if ret != 0:
                return ret-1
        if i_save == len(savelist)-1:
            return 0

def create_save_menu(game):
    options = [("Enter Name of Save",1,(127,0,255)),
               ("please notice: only letters, numbers and -_ are allowed",1),
               ("",2,(0,0,200)),
               ("Create Save",),
               ("Back",)]
    while True:
        i_option,namelist = Display.menu(options)
        save = namelist[0].replace(" ","_")
        if i_option == -1:
            return -1
        if i_option == 3:
            test = save.replace("-","").replace("_","")
            if test != "" and test.isalnum():
                ret = singleplayer(game,save+".cfg")
                if ret != 0:
                    return ret-1
        if i_option == 4:
            return 0

def singleplayer(game, save):
    gamedir = os.path.join(gamesdir,game)
    savefile = os.path.join(savedir,game,save)

    Server = server.Server(gamedir,savefile)
    #M# Menü unterschiedlich gestalten jenachdem wie viele Spieler es gibt
    # und ob das erstellen neuer Spieler erlaubt ist
    print Server.interpreter.get_var(["main","TYPES","player@objecttypes"])
    playerlist = ([("Select Player",1,(127,0,255))]+
                  [(i,) for i in Server.interpreter.get_var(["main","TYPES","player@objecttypes"]).split(",")]+
                  [("Back",)])
    i_player = Display.menu(playerlist)[0]
    if i_player == -1:
        return -1
    if i_player == len(playerlist)-1:
        return 0
    playername = playerlist[i_player][0]
    print "playername",playername

    events = []

    while not "QUIT" in [event[0] for event in events]:
        objectlist = Display.get_required_objects()
        # client -> server: events, playername, objectlist
        Server.call_events(events,playername)
        Server.update()
        displaydata = Server.get_objectdata(playername,objectlist)
        # server -> client: displaydata
        events = Display.show(displaydata,playername)

    Server.close()
    return 1

                           ###############
                           # Multiplayer #
                           ###############

def multiplayer_menu():
    servers =  socket_connection.search_servers()
    if servers == []:
        print "no servers found"
        Display.menu([("no servers found",)])
    else:
        serverlist = ([("Select Server",1,(127,0,255))]+
                      [(i[1],) for i in servers]+
                      [("Back",)])
        i_server = Display.menu(serverlist)[0]
        print i_server
        if i_server == -1:
            return -1
        elif 0 < i_server < len(serverlist)-1:
            server_addr = servers[i_server-1][0]
            ret = multiplayer(server_addr)
            if ret != 0:
                return ret-1
        elif i_server == len(serverlist):
            return 0
    return 0

def multiplayer(server):
    events = []

    client = socket_connection.client(server)

    players = client.ask(repr(["get_players","",""])).replace("\n","").replace("\r","").split(",")
    #M# Menü unterschiedlich gestalten jenachdem wie viele Spieler es gibt
    # und ob das erstellen neuer Spieler erlaubt ist
    playerlist = ([("Select Player",1,(127,0,255))]+
                  [(player,) for player in players]+
                  [("Back",)])
    i_player = Display.menu(playerlist)[0]
    if i_player == -1:
        return -1
    if i_player == len(playerlist)-1:
        return 0
    playername = playerlist[i_player][0]

    password = ""

    random_key = client.ask(repr(["random_key",playername,""]))
    random_key = random_key.replace("\n","").replace("\r","")
    combined_key = password+random_key
    hashed_combined_key = hashlib.md5(combined_key).hexdigest()
    reply = client.ask(repr(["login",playername,hashed_combined_key]))
    print reply
    if reply.startswith("access denied"):
        return

    #Display = IOlib.Display(datadir,playername,controlsfile)

    t = time.time()
    while True:
        objectlist = Display.get_required_objects()
        # client -> server: events, playername, objectlist
        request = repr([events,playername,objectlist])
        answer = client.ask(request)
        displaydata = ast.literal_eval(answer)
        # server -> client: displaydata
        if "QUIT" in [event[0] for event in events]:
            break #muss nach Datenübertragung kommen, damit server quit event noch bekommt
        events = Display.show(displaydata,playername)
        while time.time()-t<0.0625:
            time.sleep(0.001)
        t+=0.0625

    return 0


######################################################################

def ingame_menu():
    options = [("Controls",),
               ("Back",),]

if __name__ == "__main__":
    #main_menu()
    singleplayer("ShildimonCopy","krottest.cfg")
    Display.close()