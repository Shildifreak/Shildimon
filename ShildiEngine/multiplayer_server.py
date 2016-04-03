#! /usr/bin/env python

import sys
import os
import time
import thread
import random

sys.path.append(os.path.join(os.path.abspath(os.path.curdir),"modules"))

import ast

import server
import pygameIO
import socket_connection
reload(server)
reload(pygameIO)
reload(socket_connection)

try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', dest='name',help='server name')
    args = parser.parse_args()
    name = args.name
except ImportError:
    name = None
while not name:
    name = raw_input("servername: ")
    if name in (""):
        print "invalid server name"
        name = None

server_socket = socket_connection.server(name=name)

ende = False
game_running = False

def gameloop(game,save):
    global ende, Server, server_socket
    print "starting game"
    gamedir = os.path.join(os.path.abspath(os.path.curdir),"data","Spiele",game)
    savefile = os.path.join(os.path.abspath(os.path.curdir),"saves",game,save+".cfg")
    #datadir = os.path.join(os.path.abspath(os.path.curdir),"data","commondata")
    
    Server = server.Server(gamedir,savefile)
    authentificated = {}
    random_keys = {}
    print "started game"
    t = time.time()
    while game_running:
        Server.update()
        for request,addr in server_socket.receive():
            events,playername,objectlist = ast.literal_eval(request)
            if events == "get_players":
                answer = Server.interpreter.get_attribute("TYPES","player@objecttypes")
            elif events == "random_key":
                random_key = hex(random.randint(0,1000000000))
                random_keys[playername] = random_key
                answer = random_key
            elif events == "login":
                if Server.proof(playername,objectlist,random_keys[playername]):
                    authentificated[playername] = addr
                    answer = "access confirmed"
                else:
                    answer = "access denied"
            elif authentificated.get(playername,False) == addr:
                if events == "logout":
                    authentificated.pop(playername)
                    answer = "done"
                else:
                    Server.call_events(events,playername)
                    displaydata = Server.get_objectdata(playername,objectlist)
                    answer = repr(displaydata)
            else:
                answer = "[]"
            server_socket.send(answer,addr)
        time.sleep(0.0625-(time.time()-t))
        t+=0.0625
    print "stopping game"
    Server.close()
    print "stopped game"

while not ende:
    if game_running:
        state = " (running game) "
    else:
        state = " "
    t_input_request = time.time()
    command = raw_input("\n"+name+state+">>> ")
    if command == "":
        if time.time()-t_input_request > 0.1:
            print "-------------------HELP-------------------"
            print "quit  : quit program"
            if game_running:
                print "pause : pause game"
                print "save  : save game (and reload all objects)"
                print "stop  : save and stop game"
            else:
                print "start : start game"
                print "download..."
                print ""
            print "...   : ..."
            print "------------------------------------------"
    elif command == "quit":
        ende = True
    elif game_running:
        if command == "pause":
            pass
        elif command == "save":
            pass
        elif command == "stop":
            game_running = False
            time.sleep(1)
        elif command.startswith("start"):
            print "game already started"
        else:
            print "unknown command"
    else:
        if command.startswith("start"):
            game_running = True
            game = "Shildimon"
            save = "joram"
            thread.start_new(gameloop,(game,save))
            time.sleep(1)
        else:
            print "unknown command"
