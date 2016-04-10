#todo: deloading of landscapes from memory if not used
import sys
import os
import ConfigParser
import time
import math
import hashlib

import kroet
if "--reload" in sys.argv:
    reload(kroet)

class Server():
    def __init__(self, gamedir, savefile):
        self.gamedir = gamedir
        self.savefile = savefile
        objdir = os.path.join(self.gamedir,"Objectfiles")
        #defaultfile = os.path.join(self.gamedir,"default.cfg")
        self.interpreter = kroet.Interpreter(varset_func = self.varset_func,)
                                             #objdir = objdir)
        self.interpreter.open(savefile,self.gamedir)
        self.lastupdate = time.time()
        #self.interpreter.AdditionalCommandsets.append(self.landscapecommands)

    def close(self):
        self.interpreter.save()

    def update(self):
        dt = time.time()-self.lastupdate
        self.lastupdate = time.time()
        if dt == 0:
            dt = 0.001
        elif dt > 1:
            dt = 1
        #Events
        #for objekt in self.interpreter.get_attribute("UPDATE","events","").split(","):
        #    if objekt != "":
        #        events = self.interpreter.get_attribute(objekt,"events","")
        #        if events != "":
        #            events= self.interpreter.split(events)
        #            event = events[0]
        #            events = events[1:] #do not use inplace command like pop
        #            self.interpreter.set_attribute(objekt,"events",self.interpreter.list2str(events))
        #            self.interpreter.execute(event,{"object":objekt,"dt":dt})
        #Loopaction
        #for objekt in self.interpreter.objects.keys():
        for objekt in self.interpreter.filehandler.data.get("main",()): #M# only loaded objects
            if objekt != "":
                # Test whether variable is indeed object
                if not isinstance(self.interpreter.filehandler.data.get("main",{}).get(objekt,None),dict):
                    continue
                action = self.interpreter.get_attribute(objekt,"loopaction","")
                if action != "":
                    self.interpreter.execute(action,{"object":objekt,"dt":dt})

    def denest_objectlink(self,names): #resolves nested requests for objectdata
        objects = [names[0]]
        for name in names[1:]:
            new = []
            for objekt in objects:
                new.extend(self.interpreter.get_attribute(objekt,name,"",False).split(","))
            objects = new
        return objects

    def get_objectdata(self,playername,objectlist):
        objectdata = {}
        if "LANDSCAPETILES" in objectlist[:]:
            landscape = self.interpreter.get_attribute(playername,"landschaft",False)
            size = self.interpreter.get_attribute(landscape,"size",False)
            dx,dy = [int(i) for i in size.split(",")]
            for y in range(dy):
                for x in range(dx):
                    objectname = str(x)+","+str(y)+"@"+landscape[landscape.find("@")+1:]
                    objectlist.append(objectname)
        for objectdescription in objectlist:
            if objectdescription == "LANDSCAPETILES":
                pass
            else:
                description = objectdescription.split(".")
                for i in range(len(description)):
                    if description[i] == "":
                        description[i] = playername
                objectnames = self.denest_objectlink(description)
                for objectname in objectnames:
                    #objekt = self.interpreter.get_object(objectname)
                    typeobj = self.interpreter.get_attribute(objectname,"type",None)
                    if typeobj:
                        whitelist = self.interpreter.get_attribute(typeobj,"publicattrs","").split(",")
                        execlist = self.interpreter.get_attribute(typeobj,"publicexecattrs","").split(",")
                        objectdata[objectname] = {}
                        attrset = set(whitelist)
                        if "*" in whitelist:
                            attrset.update(set(objekt.iterkeys()))
                        for attr in attrset:
                            value = self.interpreter.get_attribute(objectname,attr,"")
                            if value != "":
                                if attr in execlist:
                                    objectdata[objectname][attr]=self.interpreter.execute(value,{"object":playername})
                                else:
                                    objectdata[objectname][attr]=value
                    else:
                        #objectdata[objectname] = objekt #pass for more safety
                        pass
        return objectdata

    def call_events(self,events,player):
        eventmap = self.interpreter.get_attribute(player,"eventmap")
        for event in events:
            #M# filter valid events here, for instance click events at objects not in display of player
            command = self.interpreter.get_attribute(eventmap,event[0])
            envvar = {"object":player}
            if event[0] == "move":
                varnames = ("event","dx","dy")
            elif event[0] == "dialog":
                varnames = ("event","dialog","choice")
            elif event[0] == "input":
                varnames = ("event","input")
            else:
                varnames = ("event","state","focus","x","y","fx","fy","w","h")
            for i in range(min(len(varnames),len(event))):
                envvar[varnames[i]]=event[i]
            self.interpreter.execute(command,envvar)

    def proof(self,playername,hashed_combined_key,random_key):
        password = self.interpreter.get_attribute(playername,"password")
        combined_key = password+random_key
        if hashlib.md5(combined_key).hexdigest() == hashed_combined_key:
            return True
        return False

    def varset_func(self,objekt,attribute,valueold,value):
        if attribute == "type":
            pass
        else:
            pass

