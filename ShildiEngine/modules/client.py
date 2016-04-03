import sys,os
import math
import string
import time
import ConfigParser

default_controls_info = {"left":"move to the left",
                         "right":"move to the right",
                         "up" : "move up",
                         "down": "move down",
                         "action": "ok",
                         "back": "go back",
                         "toggle": "toggle modes",
                         "toggledebug": "toggle debug screen",
                         "toggleegomode": "toggle ego mode",
                         "click" : "click at something",
                         "amx": "absolute horizontal pointer control",
                         "amy": "absolute vertical pointer control",
                         "rmx": "relative horizontal pointer control",
                         "rmy": "relative vertical pointer control",
                         }

def get(iterableobjekt,index,default):
    try:
        return iterableobjekt[index]
    except IndexError:
        return default

def escape(string):
    return '"'+string.replace('"','""')+'"'

class Display():
    def __init__(self,datapath,settings_fn):
        self.dialogs = []
        self.focusobject = None
        self.focuspos = None
        self.input = ""
        self.mode = 0 #{walk:0,dialog:1,input:2}
        self.fpstime = time.time()
        self.showdebug = False
        self.showmenu = False
        self.menustate = 0

        self.events = []
        self.keys = {"up":False,"right":False,"down":False,"left":False}
        self.new_images = []

        self.datapath = datapath
        self.settings_fn = settings_fn
        self.settings = ConfigParser.ConfigParser()
        self.settings.read(self.settings_fn)
        self.controlmaps = ["default"]
        
        IOlib_name = self.settings.get("display","module")
        while True:
            try:
                IOlib = __import__(IOlib_name)
                if "--reload" in sys.argv:
                    reload(IOlib)
            except ImportError:
                print("IOlib is not avaible")
                #M# use consoleIO for selection of other display module
                print("Falling back to default: pygameIO")
                IOlib_name = "pygameIO"
                continue
            try:
                IOlib.ShildiEngineIOlibIndicator
            except AttributeError:
                print("selected module ",IOlib," is no IO module")
                #M# use consoleIO for selection of other display module
                print("Falling back to default: pygameIO")
                IOlib_name = "pygameIO"
                continue
            break
        displaycfg = dict(self.settings.items("display"))
        self.display = IOlib.Display(datapath,displaycfg)

        self.maxfps = float(self.settings.get("display","maxfps"))
        self.t_clock = 0

    def close(self):
        width,height = self.display.get_window_size()
        self.settings.set("display","width",str(width))
        self.settings.set("display","height",str(height))
        settingsfile = open(self.settings_fn,"w")
        self.settings.write(settingsfile)
        settingsfile.close()
        self.display.close()
        
    def setmode(self,mode):
        mode %= 3
        if self.mode == 0:
            for key in self.keys.iterkeys():
                self.keys[key] = False
        self.mode = mode

    def get_required_objects(self):
        ro = ["",
              ".display",
              ".display.objects",
              "LANDSCAPETILES",
              ".dialogs",
              ]
        return ro

    def get_control(self,controlkey):
        for controlmap in self.controlmaps[::-1]:
            controlmap = self.settings.get("display","module")+"_"+controlmap+"_controls"
            if self.settings.has_section(controlmap):
                if self.settings.has_option(controlmap,controlkey):
                    return self.settings.get(controlmap,controlkey)
        return None

    def show(self,displaydata,playername):
        self.playername = playername
        self.controlmaps = ["default"]+displaydata[self.playername].get("controlmaps","").split(",")
        while "" in self.controlmaps:
            self.controlmaps.remove("")

        self.draw_displays(displaydata)
        self.draw_dialogs(displaydata)
        if self.showdebug:
            self.draw_debuginfo()

        self.display.clear()
        self.update_focus(self.display.update(self.new_images))
        self.new_images = []

        dt = time.time()-self.t_clock
        if dt < 1.0/self.maxfps:
            time.sleep(1.0/self.maxfps-dt)
        self.t_clock = time.time()

        raw_events,self.client_events = self.display.get_events()

        for raw_key,state in raw_events:
            key = self.get_control(raw_key)
            if key:
                self.client_events.append((key,state))

        if self.mode == 0:
            self.landscape_events()
        elif self.mode == 1:
            self.dialog_events()
        elif self.mode == 2:
            self.input_events()
        self.common_events()

        events = self.events
        self.events = []
        self.client_events = []
        return events

    def draw_debuginfo(self):
        t = time.time()
        fps = int(1.0/(t-self.fpstime))
        self.fpstime = t
        for text,pos in [(self.input,                  ( 50,200)),
                         (str(self.focusobject),       ( 50,300)),
                         (str(self.mode),              (200,  0)),
                         (str(len(self.display.images)),       (200, 20)), #auslagern bitte
                         (str(len(self.display.scaled_images)),(200, 30)), #dito
                         (str(fps),                    (200, 50)),
                         ]:
            self.new_images.append(("<text,%s,0,0,0,255>"%escape(text)
                                    ,pos,(None,20),None))

    def sort_tiles(self,arg1,arg2):
        #arg in format: objektname,x,y,z,...
        if arg1[3]>arg2[3]:
            return 1
        if arg1[3]!=arg2[3]: #(< and !=) means > (but hopefully faster)
            return -1
        if arg1[2]>arg2[2]:
            return 1
        if arg1[2]!=arg2[2]: #(> and !=) means < (but hopefully faster)
            return -1
        return 0

    def eval_posstr(self,string,zoom=1):
        width,height = self.display.get_window_size()
        coordinates = string.split(",")
        output = []
        for coordinate in coordinates:
            output.append(0)
            for summand in coordinate.split("+"):
                if summand.endswith("w"):
                    output[-1]+=float(summand[:-1])*width
                elif summand.endswith("h"):
                    output[-1]+=float(summand[:-1])*height
                elif summand.endswith("m"):
                    output[-1]+=float(summand[:-1])*min(height,width)
                elif summand.endswith("M"):
                    output[-1]+=float(summand[:-1])*max(height,width)
                elif summand.endswith("px"): #must be before summond.endswith(x)
                    output[-1]+=float(summand[:-2])
                elif summand.endswith("x"):
                    output[-1]+=float(summand[:-1])*self.display.get_mousepos()[0]
                elif summand.endswith("y"):
                    output[-1]+=float(summand[:-1])*self.display.get_mousepos()[1]
                elif summand != "":
                    output[-1]+=float(summand)*zoom
        return output

    def draw_displays(self,displaydata):
        zoom, = self.eval_posstr(displaydata[self.playername].get("zoom"))
        display_names = displaydata[self.playername].get("display","").split(",")
        for display_name in display_names:
            tiles = []
            display = displaydata.get(display_name,{})
            display_objects = display.get("objects","").split(",")
            centerpos = self.eval_posstr(display.get("centerpos","0,0,0"),zoom)
            for objektname in display_objects:
                objekt = displaydata[objektname]
                x,y,z = self.eval_posstr(objekt.get("position"),zoom)
                wh = self.eval_posstr(objekt.get("imagesize"),zoom)
                if len(wh) == 2:
                    w,h = wh
                else:
                    w,h = wh[0],None
                x -= centerpos[0]; y -= centerpos[1]; z -= centerpos[2]
                tiles.append((objektname,x,y,z,w,h,objekt["image"],"no frontimage"))
            if display.has_key("size"):
                display_size = [int(i) for i in display["size"].split(",")]
                landscape_name = display_name.split("@")[1]
                for x in range(display_size[0]):
                    for y in range(display_size[1]):
                        objektname = "%i,%i@%s" %(x,y,landscape_name)
                        if displaydata.has_key(objektname):
                            objekt = displaydata[objektname]
                            for z in objekt.get("heights","0").split(","):
                                tiles.append((objektname,
                                              int(x)*zoom-centerpos[0],
                                              int(y)*zoom-centerpos[1],
                                              int(z)*zoom-centerpos[2]-0.01,
                                              zoom,None,
                                              objekt.get("image",None),
                                              "no frontimage"))
            #M# if not self.display.SUPPORTS_3D_UPDATE
            tiles.sort(cmp=self.sort_tiles)
            for objektname,x,y,z,w,h,topimagestring,frontimagestring in tiles:
                width,height = self.display.get_window_size()
                imageheight = self.display.get_image_size(topimagestring,(w,h))[1]
                x2d = x+width/2
                y2d = y-imageheight+height/2
                self.new_images.append((topimagestring,
                                        (int(x2d),int(y2d)),
                                        (w,h),
                                        objektname))
                                        

    def draw_dialogs(self,displaydata):
        # muss noch viel hübscher werden
        lastdialogs = self.dialogs
        self.dialogs = displaydata[self.playername].get("dialogs","").split(",")
        if self.dialogs == [""]:
            self.dialogs = []
            if lastdialogs != self.dialogs:
                self.setmode(0)
        elif lastdialogs != self.dialogs:
            self.setmode(1)
        pos = (0,0)
        for dialog in self.dialogs:
            text = displaydata[dialog].get("text","")
            self.new_images.append(("<text,%s,0,0,0,255>"%escape(text),
                                    pos,(None,14),None))

    def landscape_events(self):
        if self.focuspos:
            fx,fy = self.focuspos
        else:
            fx,fy = None,None
        x,y = self.display.get_mousepos()
        w,h = self.display.get_window_size()
        for eventnumber in range(-len(self.client_events),0): #backwards for not destroying the loop when manipulating the list
            event,info = self.client_events[eventnumber]
            if self.keys.has_key(event):
                self.keys[event]=info
                self.client_events.pop(eventnumber)
            elif (event in ("action","back","click")) or event.startswith("custom"):
                if info != 0:
                    self.events.append((event,info,self.focusobject,x,y,fx,fy,w,h))
                    self.client_events.pop(eventnumber)
                else:
                    self.events.append(("-"+event,info,self.focusobject,x,y,fx,fy,w,h))
                    self.client_events.pop(eventnumber)
            else:
                pass
        x = 0
        y = 0
        if self.keys["up"]:
            y -= 1
        if self.keys["down"]:
            y += 1
        if self.keys["left"]:
            x -= 1
        if self.keys["right"]:
            x += 1
        if (x != 0) or (y != 0):
            self.events.append(("move",x,y))

    def dialog_events(self):
        if self.dialogs == []:
            self.mode += 1
            return
        for eventnumber in range(-len(self.client_events),0): #backwards for not destroying the loop when manipulating the list
            event,info = self.client_events[eventnumber]
            if info == True:
                if event in ("left","right","up","down"):
                    pass
                if event == "action":
                    self.events.append(("dialog",self.dialogs[-1],"0"))
                    self.client_events.pop(eventnumber)
                if event == "back":
                    self.events.append(("dialog",self.dialogs[-1],"-1"))
                    self.client_events.pop(eventnumber)
                if event == "click":
                    pass

    def input_events(self):
        for eventnumber in range(-len(self.client_events),0): #backwards for not destroying the loop when manipulating the list
            event,info = self.client_events[eventnumber]
            if event == "character":
                if info in (set(string.printable)-
                            (set(string.whitespace)-set(" "))):
                    self.input += info
            elif info == True:
                if event in ("left","right","up","down"):
                    pass
                if event == "action":
                    self.events.append(("input",self.input))
                    self.input = ""
                    if self.dialogs:
                        self.setmode(1)
                    else:
                        self.setmode(0)
                    self.client_events.pop(eventnumber)
                if event == "back":
                    if len(self.input)>0:
                        self.input = self.input[:-1]
                    self.client_events.pop(eventnumber)
                if event == "click":
                    pass

    def common_events(self):
        for eventnumber in range(-len(self.client_events),0): #backwards for not destroying the loop when manipulating the list
            event,info = self.client_events[eventnumber]
            if info == True:
                if event == "toggle":
                    self.setmode(self.mode+1)
                if event == "toggledebug":
                    self.showdebug = not self.showdebug
                if event == "menu":
                    self.showmenu = True
                    self.menustate = 0
            if event == "QUIT":
                self.events.append((event,info))

    def update_focus(self,focusobjects):
        self.focusobject = None
        self.focuspos = None
        for obj in focusobjects:
            image_name,pos,size,ID = obj[0]
            if ID != None:
                self.focusobject = ID
                self.focuspos = obj[1]


                                     ########
                                     # Menu #
                                     ########

    def menu(self,options,style=None):
        self.controlmaps.append("menu")
        options = options[:] #create copy to work with
        for i in range(len(options)):
            if type(options[i]) in (list,tuple):
                options[i] = menuoption(options[i],i)

        if style == None:
            style = self.settings.get("display","menustyle")

        dirname = os.path.join(self.datapath,"Images","Menu",style)
        cp = ConfigParser.ConfigParser()
        cp.read(os.path.join(dirname,"config.cfg"))

        i_decision = None
        selected_option = None
        selected_input = None
        self.focusobject = None
        buttondown = 0
        usingmouse = True
        mousepos = (0,0)
        mousepos_old = (0,0)
        y = 0
        backrate = 0.1
        backdelay = 0.3
        backtime = None
        while i_decision == None:
            dt = time.time()-self.t_clock
            if dt < 1.0/self.maxfps:
                time.sleep(1.0/self.maxfps-dt)
            self.t_clock = time.time()
            
            width, height = self.display.get_window_size()
            mousepos_old = mousepos
            mousepos = self.display.get_mousepos()

            #Events

            raw_events,events = self.display.get_events()
            for raw_key,state in raw_events:
                key = self.get_control(raw_key)
                if key:
                    events.append((key,state))
            for event in events:
                if event[0] == "QUIT":
                    i_decision = -1
                if event[0] == "click":
                    if event[1] == True:
                        usingmouse = True
                        buttondown = 1
                        mousepos = self.display.get_mousepos()
                        mousepos_old = mousepos
                    if event[1] == False:
                        if (buttondown < 10) and (type(self.focusobject)==int):
                            selected_option = options[self.focusobject]
                            if selected_option.type == 0:
                                i_decision = selected_option.index
                            elif selected_option.type == 2:
                                selected_input = selected_option
                        buttondown = 0
                if event[1]:
                    if (event[0] in ("up","down")):
                        usingmouse = False
                        if selected_option != None:
                            if event[0] == "down":
                                new_index = selected_option.index+1
                                if new_index > len(options)-1:
                                    new_index = len(options)-1
                            else:
                                new_index = selected_option.index-1
                                if new_index < 0:
                                    new_index = 0
                        else:
                            if event[0] == "down":
                                new_index = 0
                            else:
                                new_index = len(options)-1
                        selected_option = options[new_index]
                        if selected_option.type == 2:
                            selected_input = selected_option
                        y = -selected_option.y+height/2-selected_option.height/2
                    if event[0] == "action":
                        if selected_option != None:
                            if selected_option.type == 0:
                                i_decision = selected_option.index
                if (event[0] == "back"):
                    if event[1]:
                        backtime = time.time()+backdelay
                        if selected_input:
                            if len(selected_input.text)!=0:
                                selected_input.text=selected_input.text[:-1]
                    else:
                        backtime = None
                if event[0] == "character":
                    if selected_input:
                        if event[1] in (set(string.printable)-
                                (set(string.whitespace)-set(" "))):
                            selected_input.text+=str(event[1])
            if backtime and (backtime < time.time()):
                backtime = time.time()+backrate
                if selected_input:
                    if len(selected_input.text)!=0:
                        selected_input.text=selected_input.text[:-1]                
            if usingmouse:
                if type(self.focusobject)==int:
                    selected_option = options[self.focusobject]
                else:
                    selected_option = None
            if buttondown != 0:
                dy = mousepos[1] - mousepos_old[1]
                buttondown += float(abs(dy))*100/height
                y += dy

            #Display

            y_option = 0
            for option in options:
                if option.type == 0:
                    if option == selected_option:
                        option.imagename = cp.get("images","hlbutton")
                    else:
                        option.imagename = cp.get("images","button")
                elif option.type == 1:
                    option.imagename = cp.get("images","heading")
                elif option.type == 2:
                    option.imagename = cp.get("images","input")
                image_height = self.display.get_image_size(option.imagename,(width,None))[1]
                option.y = y_option
                option.height = image_height
                y_option += image_height

            if y_option <= height:
                y = (height-y_option)/2
            elif y > 0:
                y = 0
            elif y < height-y_option:
                y = height-y_option

            for option in options:
                #M# "#tmp,<text..."
                optiontext = "<text,%s,%i,%i,%i,%i>" %(
                    (escape(option.text),)+option.color)
                self.new_images.append((option.imagename,(0,option.y+y),
                                       (width, option.height),None))
                self.new_images.append((optiontext,(0.1*width,option.y+y),
                                       (0.8*width,option.height),option.index))

            self.update_focus(self.display.update(self.new_images))
            self.new_images = []
            self.display.clear()

        self.display.clear_cache()
        self.controlmaps.remove("menu")
        return i_decision,[option.text for option in options if option.type==2]

    def virtual_keyboard(self):
        pass
        #s. Test

class menuoption():
    def __init__(self,args,index=None):
        """text[,type[,(r,g,b[,a])]]
type:{0:button,1:heading,2:input}"""
        self.text = args[0]
        self.type = get(args,1,0)
        self.color = get(args,2,(0,0,0,255))
        if len(self.color)==3:
            self.color += (255,)
        self.imagename = None
        self.height = None
        self.y = None
        self.index = index

    def __init2__(self):
        self.text = ""
        self.style = "default"
        self.color = (0,0,0,255)
        self.imagename = None
        self.height = None
        self.y = None
        self.index = index

        self.editable_text = False
        self.l_arrow = False
        self.r_arrow = False

    def left(self):
        pass

    def right(self):
        pass

    def click(self):
        pass

class menuButton(menuoption):
    def __init__(self,text,action=None):
        menuoption.__init__(self)
        self.style = "button"
        if type(action) == type(lambda:None):
            self.click = action
        else:
            self.click = lambda text=action:text

if __name__ == "__main__":
    d = Display("../data/commondata","../saves/settings.cfg")
    while True:
        result = d.menu([#("Singleplayer",),
                         #("Multiplayer",),
                         #("HEADING",1,),
                         #("Input...",2,(0,0,255)),
                         #("login",2,(0,0,0,0)),
                         #(u"und ganz viele weitere sinnlose Einträge",0,(255,0,0)),
                         ("Ende",)])
        print result
        if result[0] in (-1,6):
            break
    d.close()
