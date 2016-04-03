import time
import math
import random

def tmpoffsetfunc((interpreter,envvar),xyz):
    x,y,z = xyz.split(",")
    return x+"+0.5,"+y+"+-0.5,"+z

def dummi(*args):
    return None

def printfunc((interpreter,envvar),p):
    print p
    return p

def returndot((interpreter,envvar)):
    return "."

def return_values((interpreter,envvar),*arg):
    return interpreter.list2str(arg)

def add((interpreter,envvar),num1,num2):
    return num1+num2

def sub((interpreter,envvar),num1,num2):
    return num1-num2

def mul((interpreter,envvar),num1,num2):
    return num1*num2

def div((interpreter,envvar),num1,num2):
    return 1.0*num1/num2

def mod((interpreter,envvar),num1,num2):
    return num1%num2

def int_func((interpreter,envvar),num):
    return int(num)

def sin((interpreter,envvar),angle): #angle in parts of one
    return math.sin(angle*2*math.pi)

def cos((interpreter,envvar),angle):
    return math.cos(angle*2*math.pi)

def atan2((interpreter,envvar),x,y):
    return math.atan2(x,y)/(2*math.pi)

def time_func((interpreter,envvar),faktor = 1):
    return time.time()*faktor

def hours((interpreter,envvar)):
    return time.localtime().tm_hour

def minutes((interpreter,envvar)):
    return time.localtime().tm_min

def seconds((interpreter,envvar)):
    return time.localtime().tm_sec

def varset((interpreter,envvar),varname,value):
    if varname.count(".") == 1:
        obj, attr = varname.split(".")
        return interpreter.set_attribute(obj,attr,value)
    print "could not set variable",varname

def var((interpreter,envvar),*args):
    if len(args) == 1:
        obj, attr = args[0].split(".")
    elif len(args) == 2:
        obj, attr = args[:2]
    return interpreter.get_attribute(obj,attr)
    print "could not read variable",varname

def envvar((interpreter,envvar),varname):
    return envvar.get(varname,"none")


def isequal((interpreter,envvar),*args):
    arg0 = str(args[0])
    for arg in args[1:]:
        if str(arg) != arg0:
            return False
    return True

def wenn((interpreter,envvar),boolean,iftrue,iffalse):
    if boolean in [True,"true","True"]:
        return interpreter.execute(iftrue,envvar)
    else:
        return interpreter.execute(iffalse,envvar)

def case((interpreter,envvar),*args):
    pass
    
def addevent((interpreter,envvar),event,obj=None,index=-1):
    if obj == None:
        obj = envvar["object"]
    events = interpreter.split(interpreter.get_attribute(obj,"events",""))
    while "" in events:
        events.remove("")
    events = events[:index]+[event]+events[index:] #do not use inplace transformation at this point!
    interpreter.set_attribute(obj,"events",interpreter.list2str(events))

def getlistattr((interpreter,envvar),obj,attr,index):
    pass

def setlistattr((interpreter,envvar),obj,attr,index,value):
    pass

def add2listattr((interpreter,envvar),attr,value,obj=None,index=-1):
    if obj == None:
        obj = envvar["object"]
    interpreter.add2listattr(obj,attr,value,index)

def delfromlistattr((interpreter,envvar),attr,value,obj=None,index=-1):
    if obj == None:
        obj = envvar["object"]
    interpreter.delfromlistattr(obj,attr,value,index)

def crode((interpreter,envvar),name,*parameter):
    for i in range(len(parameter)):
        envvar["PARAMETER"+str(i+1)]=parameter[i]
    #M# test code ersetzen
    print "crode",name,envvar

def update_movement((interpreter,envvar),objekt=None):
    if not objekt:
        objekt = envvar.get("object",None)
    if not objekt:
        return False
    target = interpreter.get_attribute(objekt,"target-position")
    pos = interpreter.get_attribute(objekt,"position")
    if target:
        x,y,z = [float(i) for i in pos.split(",")]
        tx,ty,tz = [float(i) for i in target.split(",")]
        max_speed = float(interpreter.get_attribute(objekt,"max-speed"))
        dt = envvar.get("dt")
        dx,dy,dz = (tx-x,ty-y,tz-z)
        d = math.sqrt(dx**2+dy**2+dz**2)
        if max_speed*dt < d:
            dx,dy,dz = [i/d*max_speed*dt for i in (dx,dy,dz)]
        else:
            interpreter.set_attribute(objekt,"target-position","")
        newpos = (x+dx,y+dy,z+dz)
        interpreter.set_attribute(objekt,"position",interpreter.list2str(newpos))
    elif pos:
        x,y,z = [float(i) for i in pos.split(",")]
        vx,vy,vz = [float(i) for i in interpreter.get_attribute(objekt,"velocity").split(",")]
    
def set_movement((interpreter,envvar),objekt=None,dx=None,dy=None):
    if not objekt:
        objekt = envvar.get("object",None)
    if not dx:
        dx = envvar.get("dx",None)
    if not dy:
        dy = envvar.get("dy",None)
    dx,dy = float(dx),float(dy)
    if abs(dx) > 1:
        dx = 2*(dx>1)-1
    if abs(dy) > 1:
        dy = 2*(dy>1)-1
    dialogs = interpreter.get_attribute(objekt,"dialogs").split(",")
    while "" in dialogs:
        dialogs.remove("")
    for dialog in dialogs:
        if interpreter.get_attribute(dialog,"block-setmove")=="true":
            return False
    movetype = interpreter.get_attribute(objekt,"movetype")
    target = interpreter.get_attribute(objekt,"target-position")
    if movetype == "grid":
        if not target:
            pos = interpreter.get_attribute(objekt,"position")
            x,y,z = [int(round(float(i))) for i in pos.split(",")]
            dx = int(round(dx)); dy = int(round(dy))
            if dx!=0 and dy!=0:
                dx = 0 #M# abwechselnd null machen (orientierung abfragen)
            x += dx; y += dy
            landscape = interpreter.get_attribute(objekt,"landschaft")
            fieldname = str(x)+","+str(y)+"@"+landscape.split("@")[1]
            hitbox = interpreter.get_attribute(fieldname,"hitbox")
            hitbox = interpreter.execute(hitbox,{"object":objekt,"x":x,"y":y,"z":z})
            if hitbox == "":
                interpreter.set_attribute(objekt,"target-position",interpreter.list2str((x,y,z)))
            #enteraction also if not entered?
            enteraction = interpreter.get_attribute(fieldname,"enter")
            interpreter.execute(enteraction,{"object":objekt,"x":x,"y":y,"z":z})

# v---- not yet in dict of functions ----v #

def uoid((interpreter,envvar)):
    idnum = random.getrandbits(32) #maybe replace this by incrementing number saved in some object
    return "ID"+hex(int(idnum))

def join((interpreter,envvar),*args):
    return "".join(str(i) for i in args)

def text((interpreter,envvar),message,action_next="",action_esc=None,objekt=None):
    if action_esc == None:
        action_esc = action_next
    if not objekt:
        objekt = envvar.get("object","")
    dialog = create_object((interpreter,envvar),uoid((interpreter,envvar)))
    #closeaction= "close_dialog(%s,%s)" %s (objekt,dialog)
    #action_next= "(%s,%s)" %s (closeaction,action_next)
    #action_esc = "(%s,%s)" %s (closeaction,action_esc)
    actions = action_esc+","+action_next
    interpreter.add2listattr(objekt,"dialogs",dialog)
    interpreter.set_attribute(dialog,"type","dialog@objecttypes")
    interpreter.set_attribute(dialog,"dialogtype","message")
    interpreter.set_attribute(dialog,"text",message)
    interpreter.set_attribute(dialog,"single-use","true")
    interpreter.set_attribute(dialog,"block-setmove","true")
    interpreter.set_attribute(dialog,"actions",actions)

    # Erstelle ein Dialogobject vom typ messagebox mit message und actionen und trage es beim aktuellen Spieler ein
    return dialog

def create_object((interpreter,envvar),name):
    interpreter.create_object(name)
    return name

def delete_object((interpreter,envvar),name):
    interpreter.delete_object(name)
    return name

def handle_dialogevent((interpreter,envvar),dialog=None,choice=None,objekt=None):
    if not objekt:
        objekt = envvar.get("object","")
    if not dialog:
        dialog = envvar.get("dialog","")
    if not choice:
        choice = envvar.get("choice","")
    actions = interpreter.split(interpreter.get_attribute(dialog,"actions"))
    action = actions[int(choice)+1]
    close_dialog((interpreter,envvar),objekt,dialog)
    interpreter.execute(action,envvar)

def close_dialog((interpreter,envvar),objekt,dialog):
    interpreter.delfromlistattr(objekt,"dialogs",dialog)
    if interpreter.get_attribute(dialog,"single-use")=="true":
        interpreter.delete_object(dialog)

def handle_clickevent((interpreter,envvar)):
    focus = envvar.get("focus",None)
    action = ""
    if focus:
        action = interpreter.get_attribute(focus,"clickaction")
    if action != "":
        interpreter.execute(action,envvar)
    else:
        pass

def handle_releaseclickevent((interpreter,envvar),*args):
    print args
    print "release click"

commands = {"tmpoffsetfunc":tmpoffsetfunc,
            #""     : return_values,
            # math
            "add"  : add ,
            "sub"  : sub ,
            "mul"  : mul ,
            "div"  : div ,
            "mod"  : mod ,
            "int"  : int_func,
            "sin"  : sin ,
            "cos"  : cos ,
            "atan2": atan2,
            "isequal" : isequal,
            # misc
            "print": printfunc ,
            "uoid" : uoid ,
            "time" : time_func,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "crode" : crode,
            "return_values": return_values,
            "join" : join,
            #> execute()
            # objects rw
            "var"  : var ,
            "varset"  : varset,
            "envvar"  : envvar,
            "create_object": create_object,
            "delete_object": delete_object,
            # game mechanics
            "update_movement": update_movement,
            "set_movement": set_movement,
            "text" : text ,
            "handle_dialogevent" : handle_dialogevent,
            "close_dialog" : close_dialog,
            "handle_clickevent" : handle_clickevent,
            "handle_-clickevent" : handle_releaseclickevent,
            #M# "addevent": addevent,
            }

if __name__ == "__main__":
    for name,value in globals().items():
        if str(type(value)) != "<type 'function'>":
            continue
        if value not in commands.values():
            print name
    for name,value in commands.items():
        if str(type(value)) != "<type 'function'>":
            continue
        if value not in globals().values():
            print name