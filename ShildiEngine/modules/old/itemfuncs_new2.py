# -*- coding: utf-8 -*-
import pygame, ConfigParser
import pygame.locals as pgl
import os, time
import pygame_menuerstellen

sep = os.path.sep

def itemmenu(itemlist,bgfile,itemimgspath,bgedit,fullscreen=False,extinv=None):
    print("startet menu")

    pygame.init()
    if fullscreen:
        screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption('Itemmenu')
    pygame.mouse.set_visible(True)
    
    mainClock = pygame.time.Clock()

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    bgimage = pygame.image.load(bgfile)
    bgimgrect=bgimage.get_rect(centerx=background.get_width()/2,
                               centery=background.get_height()/2)
    bgeditimage  = pygame.image.load(bgedit)
    bgeditimgrect=bgeditimage.get_rect(
                               centerx=background.get_width()/2,
                               centery=background.get_height()/2)

    fixpoints=[(0,0)]
    items={}
    items["lefthand"]="None"
    items["righthand"]="None"
    for x in range(17):
        for y in range(9):
            items[str(x)+","+str(y)]="None"
    
    itemstores_to_pos={"lefthand": ( 50, 50),
                       "righthand":(350, 50)}
    for x in range(17):
        for y in range(9):
            itemstores_to_pos[str(x)+","+str(y)]=( 37+x*25,
                                                  234+y*25)
    pos_to_itemstores={( 50, 50):"lefthand",
                       (350, 50):"righthand"}
    for x in range(17):
        for y in range(9):
            pos_to_itemstores[( 37+x*25,234+y*25)]=str(x)+","+str(y)

    # Zusätzliche Felder,zb. von Truhen
    if extinv:
        for i in range(len(extinv)):
            feldliste=extinv[1]
            position=extinv[0]
            for feld in feldliste:
                x,y=feld
                a,b=position[0]*800,position[1]*480
                c,d=position[0]*100,position[1]*100
                fixpoints.append((-a,-b))
                items[str(x+c)+","+str(y+d)]="None"
                pos_to_itemstores[(a+x*25,b+y*25)]=str(x+c)+","+str(y+d)
                itemstores_to_pos[str(x+c)+","+str(y+d)]=(a+x*25,b+y*25)

    items.update(itemlist)

    #print itemstores_to_pos,pos_to_itemstores

    edititems = {1:"None",2:"None",3:"None",4:"None",5:"None"}
    pos_to_editstores={(525,65) :1,
                       (635,65) :2,
                       (525,180):3,
                       (635,180):4,
                       (525,320):5,
                       }
    editstores_to_pos={1:(525,65) ,
                       2:(635,65) ,
                       3:(525,180),
                       4:(635,180),
                       5:(525,320),
                       }
    mouseshape="None"
    lastitem="None"
    mode="normal"
    page=(0,0)
    shapes={}
    mouseturn="0"

    def rotate90(shape):
        l=shape.split("|")
        for i in range(len(l)):
            l[i]=list(l[i])
            l[i].reverse()
        x=len(l[0])
        y=len(l)
        l2=[]
        for a in range(x):
            l2.append([])
            for b in range(y):
                l2[-1].append("")
        for a in range(x):
            for b in range(y):
                l2[a][b]=l[b][a]
        shape=""
        for a in l2:
            for b in a:
                shape+=b
            shape+="|"
        return shape[:-1]

    def getshape(item):
        if item in shapes.keys():
            return shapes[item]
        configleser = ConfigParser.ConfigParser()
        configleser.read(itemimgspath+item[:-1]+sep+"config.cfg")
        shape=configleser.defaults()["shape"]
        rotate=int(item[-1:])
        for i in range(rotate):
            shape=rotate90(shape)
        shapes[item]=shape
        return shape
    
    def update():
        screen.fill((0,0,0))
        for pos in pos_to_itemstores.keys():
            pygame.draw.rect(screen,(100,100,100),
                             (pos[0]+page[0],pos[1]+page[1],25,25))
        if mode=="normal":
            background.blit(bgimage,bgimgrect)
        elif mode=="edit":
            background.blit(bgeditimage,bgeditimgrect)
        for itemstore in itemstores_to_pos.keys():
            item=items[itemstore]
            if item!="None" and itemstore != mouseshape:
                if itemstore in ("righthand","lefthand"):
                    background.blit(
                    pygame.image.load(itemimgspath+item[:-1]+sep+"image.png"),
                    itemstores_to_pos[itemstore])
                else:
                    shape=getshape(item)
                    if shape.find("|")!=-1:
                        x=int((shape.find("+")+1)%(shape.find("|")+1))-1
                        y=int((shape.find("+")+1)/(shape.find("|")+1))
                    else:
                        x=shape.find("+")
                        y=0
                    #print (shape.find("+")+1),(shape.find("|")+1),x,y
                    #print itemstore
                    imagepos=(itemstores_to_pos[itemstore][0]-25*x,
                              itemstores_to_pos[itemstore][1]-25*y)
                    rotate=int(item[-1:])*90
                    if 0<imagepos[0]<800 and 0<imagepos[1]<480:
                        background.blit(
                        pygame.transform.rotate(
                        pygame.image.load(itemimgspath+item[:-1]+sep+"shape.png"),
                        rotate),
                        imagepos)
                    else:
                        screen.blit(
                        pygame.transform.rotate(
                        pygame.image.load(itemimgspath+item[:-1]+sep+"shape.png"),
                        rotate),
                        (imagepos[0]+page[0],imagepos[1]+page[1]))
        if mode=="edit":
            for editstore in editstores_to_pos.keys():
                item=edititems[editstore]
                if item!="None" and editstore != mouseshape:
                    background.blit(
                        pygame.image.load(itemimgspath+item[:-1]+sep+"image.png"),
                        editstores_to_pos[editstore])
        

    update()
    screen.blit(background,page)
    pygame.display.update()

    def movepage():
        absmousepos=mousepos[0]+page[0],mousepos[1]+page[1]
        #print absmousepos
        d=50
        if absmousepos[0]<10:
            return (page[0]+d,page[1]),(mousepos[0]-d,mousepos[1]),True
        elif absmousepos[0]>790:
            return (page[0]-d,page[1]),(mousepos[0]+d,mousepos[1]),True
        elif absmousepos[1]<10:
            return (page[0],page[1]+d),(mousepos[0],mousepos[1]-d),True
        elif absmousepos[1]>470:
            return (page[0],page[1]-d),(mousepos[0],mousepos[1]+d),True
        else:
            return page, mousepos, False

    def arrangepage():
        #fixpoints=[(0,0),(100,0)]
        nearest=None
        for point in fixpoints:
            d2 = (page[0]-point[0])**2+(page[1]-point[1])**2
            if not nearest:
                nearest=(d2,point)
            elif nearest[0]>d2:
                nearest=(d2,point)
        if d2<=1:
            return page
        return (page[0]-(page[0]-nearest[1][0])/2,
                page[1]-(page[1]-nearest[1][1])/2)

    def setinfobox(pos):
        configleser = ConfigParser.ConfigParser()
        describtion=""
        image=None
        shownitem="None"
        lastitem="None"
        for x,y in pos_to_itemstores.keys():
            if x<mousepos[0]<x+25 and y<mousepos[1]<y+25:
                item=items[pos_to_itemstores[(x,y)]]
                if item!="None":
                    shownitem=item
                    lastitem=pos_to_itemstores[(x,y)]
                    Configfile=itemimgspath+item[:-1]+sep+"config.cfg"
                    configleser.read(Configfile)
                    describtion = configleser.defaults()["describtion"]
                    image=pygame.image.load(itemimgspath+item[:-1]+sep+"image.png")

        update()
        if image:
            background.blit(image,(520,65))
            font = pygame.font.Font(None, 36)
            text = []
            l=17
            while len(describtion)>l:
                l2=l
                if describtion[:l].rfind(" ")!=-1:
                    l2=describtion[:l].rfind(" ")
                    text.append(describtion[:l2+1])
                    describtion=describtion[l2+1:]
                else:
                    text.append(describtion[:l2])
                    describtion=describtion[l2:]
            text.append(describtion)
            for zeilennummer in range(len(text)):
                zeile = text[zeilennummer]
                zeile = font.render(zeile.decode("utf8"),1,(255,255,255))
                textpos = zeile.get_rect(centerx=620,
                                     centery=200+zeilennummer*30)
                background.blit(zeile, textpos)
            describtion
        screen.blit(background,page)
        return lastitem
        

    def setmouseshape(pos,mode,edititems,lastitem,items):
        print(pos)
        for x,y in pos_to_itemstores.keys():
            if pos_to_itemstores[(x,y)]in("righthand","lefthand"):
                if x<pos[0]<x+100 and y<pos[1]<y+100:
                    return pos_to_itemstores[(x,y)], mode,edititems,lastitem,items
            elif items[pos_to_itemstores[(x,y)]]!="None":
                shape = getshape(items[pos_to_itemstores[(x,y)]])
                if shape.find("|")!=-1:
                    xl=shape.find("|")
                    yl=len(shape)/(shape.find("|")+1)+1
                    xo=int((shape.find("+")+1)%(shape.find("|")+1))-1
                    yo=int((shape.find("+")+1)/(shape.find("|")+1))
                else:
                    xl=len(shape)
                    yl=1
                    xo=shape.find("+")
                    yo=0
                print xo,yo
                for xd in range(xl):
                    for yd in range(yl):
                        if shape[xd+yd*(xl+1)] in"x+":
                            if 0<pos[0]<800 and 0<pos[1]<480:
                                if int(round(pos[0]*4,-2)/4)-13==x+(xd-xo)*25 and int(round(pos[1]*4,-2)/4)-16==y+(yd-yo)*25:
                                    return pos_to_itemstores[(x,y)], mode,edititems,lastitem,items
                            else:
                                if int(round((pos[0]-13)*4,-2)/4)==x+(xd-xo)*25 and int(round((pos[1]-7)*4,-2)/4)-5==y+(yd-yo)*25:
                                    return pos_to_itemstores[(x,y)], mode,edititems,lastitem,items
        if mode == "normal":
            if 640<pos[0]<745 and 60<pos[1]<95:
                pass #einsetzen
            if 640<pos[0]<745 and 105<pos[1]<135:
                mode=changemode(mode,edititems)
        elif mode == "edit":
            for x,y in pos_to_editstores.keys():
                if x<pos[0]<x+100 and y<pos[1]<y+100:
                    return pos_to_editstores[(x,y)], mode,edititems,lastitem,items
            if 640<pos[0]<745 and 320<pos[1]<350:
                edititems=mergeitems(edititems)
            if 640<pos[0]<745 and 400<pos[1]<430:
                mode=changemode(mode,edititems)
            if 640<pos[0]<745 and 360<pos[1]<390:
                items=divideitem(items)
                lastitem="None"
            
        return "None", mode, edititems,lastitem,items

    def changeitems(pos,items,edititems,mode):
        changed=False
        if mouseshape == "None":
            return items,edititems
        for x,y in pos_to_itemstores.keys():
            if pos_to_itemstores[(x,y)]in("righthand","lefthand"):
                size=100
            else:
                size=25
            if x<=mousepos[0]<x+size and y<=mousepos[1]<y+size and items[pos_to_itemstores[(x,y)]]=="None" and pos_to_itemstores[(x,y)]in("righthand","lefthand"):
                if mouseshape in items.keys():
                    items[pos_to_itemstores[(x,y)]]=items[mouseshape]
                    items[mouseshape]="None"
                elif mouseshape in edititems.keys():
                    items[pos_to_itemstores[(x,y)]]=edititems[mouseshape]
                    edititems[mouseshape]="None"
                changed=True
            elif x<=mousepos[0]<x+size and y<=mousepos[1]<y+size and (items[pos_to_itemstores[(x,y)]]=="None" or pos_to_itemstores[(x,y)]==mouseshape):
                print "mouseshape:",mouseshape
                if mouseshape in items.keys():
                    shape = getshape(items[mouseshape])
                elif mouseshape in edititems.keys():
                    shape = getshape(edititems[mouseshape])
                fields = []
                if shape.find("|")!=-1:
                    xl=shape.find("|")
                    yl=len(shape)/(shape.find("|")+1)+1
                    xo=int((shape.find("+")+1)%(shape.find("|")+1))-1
                    yo=int((shape.find("+")+1)/(shape.find("|")+1))
                else:
                    xl=len(shape)
                    yl=1
                    xo=shape.find("+")
                    yo=0
                for xd in range(xl):
                    for yd in range(yl):
                        if shape[xd+yd*(xl+1)] in "x+":
                            fields.append((x+(xd-xo+1)*25,y+(yd-yo+1)*25))
                #print fields
                if mouseshape in items.keys():
                    itemzwischenspeicher=items[mouseshape]
                    items[mouseshape]="None"
                elif mouseshape in edititems.keys():
                    itemzwischenspeicher=edititems[mouseshape]
                    edititems[mouseshape]="None"
                
                #Überprüfung mittels selber Routine wie beim anklicken
                blocked=False
                for pos in fields:
                    #if not (50<pos[0]<480 and 250<pos[1]<460):
                    #    print "dfghgteserg"
                    #    blocked=True
                    drinne=False
                    for x3,y3 in pos_to_itemstores.keys():
                        if (x3<pos[0]<=x3+25 and y3<pos[1]<=y3+25):
                            drinne=True
                    if not drinne:
                        blocked=True
                    for itemstore in itemstores_to_pos.keys():
                        x2,y2 = itemstores_to_pos[itemstore]
                        if not itemstore==mouseshape:
                            if pos_to_itemstores[(x2,y2)]in("righthand","lefthand"):
                                if x2<pos[0]<x2+100 and y2<pos[1]<y2+100:
                                    blocked=True
                            elif items[pos_to_itemstores[(x2,y2)]]!="None":
                                shape=getshape(items[pos_to_itemstores[(x2,y2)]])
                                if shape.find("|")!=-1:
                                    xl=shape.find("|")
                                    yl=len(shape)/(shape.find("|")+1)+1
                                    xo=int((shape.find("+")+1)%(shape.find("|")+1))-1
                                    yo=int((shape.find("+")+1)/(shape.find("|")+1))
                                else:
                                    xl=len(shape)
                                    yl=1
                                    xo=shape.find("+")
                                    yo=0

                                #print xo,yo
                                for xd in range(xl):
                                    for yd in range(yl):
                                        if shape[xd+yd*(xl+1)] in"x+":
                                            if 0<pos[0]<800 and 0<pos[1]<480:
                                                if int(round(pos[0]*4,-2)/4)-13==x2+(xd-xo)*25 and int(round(pos[1]*4,-2)/4)-16==y2+(yd-yo)*25:
                                                    blocked=True
                                            else:
                                                if int(round((pos[0]-13)*4,-2)/4)==x2+(xd-xo)*25 and int(round((pos[1]-20)*4,-2)/4)-5==y2+(yd-yo)*25:
                                                    blocked=True
                print "blocked:",blocked
                if not blocked:
                    items[pos_to_itemstores[(x,y)]]=itemzwischenspeicher
                    changed=True
                else:
                    if mouseshape in items.keys():
                        items[mouseshape]=itemzwischenspeicher
                    elif mouseshape in edititems.keys():
                        edititems[mouseshape]=itemzwischenspeicher

        if mode == "edit":
            for x,y in pos_to_editstores.keys():
                if x<mousepos[0]<x+100 and y<mousepos[1]<y+100:
                    if mouseshape in edititems.keys():
                        item1=edititems[mouseshape]
                        item2=edititems[pos_to_editstores[(x,y)]]
                        edititems[mouseshape]=item2
                        edititems[pos_to_editstores[(x,y)]]=item1
                        changed=True
                    elif mouseshape in ("lefthand","righthand"):
                        item1=items[mouseshape]
                        item2=edititems[pos_to_editstores[(x,y)]]
                        items[mouseshape]=item2
                        edititems[pos_to_editstores[(x,y)]]=item1
                        changed=True
                    elif mouseshape in items.keys():
                        if edititems[pos_to_editstores[(x,y)]]=="None":
                            edititems[pos_to_editstores[(x,y)]]=items[mouseshape]
                            items[mouseshape]="None"
                            changed=True

        if changed == False:
            if mouseshape in items.keys():
                #print "mouseturn:", mouseturn
                items[mouseshape]=items[mouseshape][:-1]+mouseturn

        return items,edititems

    def changemode(mode,edititems):
        for i in edititems.values():
            if i != "None":
                return mode
        if mode=="normal":
            return "edit"
        else:
            return "normal"
    
    def mergeitems(edititems):
        print "merge",edititems
        configleser = ConfigParser.ConfigParser()
        options=[]
        for ordner in os.listdir(itemimgspath):
            configleser.read(itemimgspath+ordner+sep+"config.cfg")
            l = configleser.defaults()["tiles"].split(",")
            l2 = edititems.values()
            for i in range(5):
                if "None" in l2:
                    l2.remove("None")
            for i in range(len(l2)):
                l2[i]=l2[i][:-1] # Zahl für Richtung kürzen
            if set(l).symmetric_difference(set(l2))==set():
                #print configleser.defaults()["name"]
                options.append(configleser.defaults()["name"])
        if options==[]:
            return edititems
        menulist=[]
        for item in options:
            menulist.append((item,item))
        item = pygame_menuerstellen.openmenu(menulist,
                                             closeafterticking=True,
                                             screen=screen)+"0"
        pygame.mouse.set_visible(True)
        edititems = {1:"None",2:"None",3:"None",4:"None",5:item}
        print edititems
        
        return edititems

    def divideitem(items):
        if edititems[5] == "None":
            return items
        print "divide",edititems[5]
        configleser = ConfigParser.ConfigParser()
        print itemimgspath+edititems[5][:-1]+sep+"config.cfg"
        configleser.read(itemimgspath+edititems[5][:-1]+sep+"config.cfg")
        tiles = configleser.defaults()["tiles"].split(",")
        freeplace=1+edititems.values().count("None")
        if tiles==[""]:
            return items
        if freeplace == 5:#freeplace >= len(tiles):
            edititems[5]="None"
            for itemstore in edititems.keys():
                if edititems[itemstore]=="None" and len(tiles)>0:
                    edititems[itemstore]=tiles.pop()+"0"
        return items

    # LOOP
    print("start loop")
    end = False
    mousepos=(400,240)
    timer=pygame.time.Clock()
    while not end:
        pygame.time.Clock().tick(16)
        # check for events
        events=pygame.event.get()
        for event in events:
            if mode=="normal":
                if event.type == pgl.QUIT:
                    end=True
                if event.type == pgl.KEYUP:
                    end=True
            if event.type == pgl.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseshape,mode,edititems,lastitem,items = setmouseshape(
                        mousepos,mode,edititems,lastitem,items)
                    if mouseshape in (1,2,3,4,5):
                        mouseturn=edititems[mouseshape][-1:]
                    elif mouseshape in items.keys():
                        mouseturn=items[mouseshape][-1:]
                    else:
                        mouseturn="0"
                    print "mouseturn1:", mouseturn
                    update()
                    screen.blit(background,page)
                    pygame.display.update()
                    #print mode
                if event.button == 3 and mouseshape!="None":
                    if mouseshape in (1,2,3,4,5):
                        rotate=int(edititems[mouseshape][-1:])
                        #print rotate
                        rotate=(rotate+1)%4
                        edititems[mouseshape]=edititems[mouseshape][:-1]+str(rotate)
                    else:
                        rotate=int(items[mouseshape][-1:])
                        #print rotate
                        rotate=(rotate+1)%4
                        items[mouseshape]=items[mouseshape][:-1]+str(rotate)
            if event.type == pgl.MOUSEBUTTONUP:
                if event.button == 1:
                    items,edititems=changeitems(mousepos,items,edititems,mode)
                    mouseshape = "None"
            if event.type == pgl.MOUSEMOTION:
                mousepos = event.pos[0]-page[0],event.pos[1]-page[1]

        page,mousepos,chbool=movepage()
        if not chbool:
            page=arrangepage()
        if mode == "normal":
            lastitem = setinfobox(mousepos)
        else:
            update()
            screen.blit(background,page)
        
        if mouseshape in (1,2,3,4,5):
            mouseitem=edititems[mouseshape]
        elif mouseshape and mouseshape!="None":
            mouseitem=items[mouseshape]
        else:
            mouseitem="None"
        if mouseitem!="None":
            #HIER MUSS STATTDESSEN EINE RELATIVE ANGABE IN BEZUG AUF ITEMPOS HIN
            imagesort="image.png"
            for x,y in pos_to_itemstores.keys():
                if x<=mousepos[0]<=x+25 and y<=mousepos[1]<=y+25:
                    imagesort="shape.png"
            if imagesort=="shape.png":
                shape=getshape(mouseitem)
                if shape.find("|")!=-1:
                    x=int((shape.find("+")+1)%(shape.find("|")+1))-1
                    y=int((shape.find("+")+1)/(shape.find("|")+1))
                else:
                    x=shape.find("+")
                    y=0
                #print (shape.find("+")+1),(shape.find("|")+1),x,y
                imagepos=(mousepos[0]-13-25*x+page[0],
                          mousepos[1]-13-25*y+page[1])
                rotate=int(mouseitem[-1:])*90
            else:
                imagesort="image.png"
                imagepos=(mousepos[0]-50+page[0],mousepos[1]-50+page[1])
                rotate=0
            screen.blit(
                pygame.transform.rotate(
                    pygame.image.load(itemimgspath+mouseitem[:-1]
                                    +sep+imagesort),rotate)
                ,imagepos)
        pygame.display.update()

    extitems = {}
    for item in items.items():
        if item[1]=="None":# and item[0] not in ("righthand","lefthand"):
            items.pop(item[0])
        elif item[0] not in ("righthand","lefthand"):
            x,y = [int(i) for i in item[0].split(",")]
            if not (0<=x<17 and 0<=y<9):
                print x,y
                extitems[item[0]]=items.pop(item[0])

    return items, extitems



def itemsurface(items,itemimgspath):
    pygame.init()
    background = pygame.Surface((800,480))
    background = background.convert_alpha()
    #background.set_alpha(100)
    #pygame.Surface.set_alpha()    #set_alpha(100)
    #background = background.convert()
    background.fill((0,0,0,0))
    itemr=items.get("righthand","None")
    iteml=items.get("lefthand","None")
    background.blit(pygame.image.load(itemimgspath+"bg.png"),(0,0))
    background.blit(pygame.image.load(itemimgspath+"bg.png"),(671,0))
    if iteml!="None":
        background.blit(
            pygame.image.load(itemimgspath+iteml[:-1]+sep+"image.png"),
                              (11,10))
    if itemr!="None":
        background.blit(
            pygame.image.load(itemimgspath+itemr[:-1]+sep+"image.png"),
                              (682,10))
    return background



if __name__=="__main__":
    itemlist={}
    itemlist["lefthand"]="Beil0"
    itemlist["righthand"]="Axt0"
    itemlist["5,4"]="Flasche_Wasser0"
    #itemlist["4,1"]="Leine"
    #itemlist["8,1"]="Magnet"
    itemlist["12,1"]="Schwert2"
    itemlist["16,2"]="Beere0"
    itemlist["1,1"]="Schwert1"
    itemlist["15,7"]="Schwert0"
    itemlist["1,-99"]="Beere0"
    itemlist["4,-96"]="Schwert1"
    extinvposlist=[]
    for x in range(1,11):
        for y in range(1,11):
            extinvposlist.append((x,y))
    extinvposlist.remove((5,5))
    extinv=((0,-1),extinvposlist)

    items,extitems=itemmenu(itemlist,
                            "..%sdata%sother%sNew_Itemmenubackground.png" %(sep,sep,sep),
                            "..%sdata%sObjekte%sItems%s" %(sep,sep,sep,sep),
                            "..%sdata%sother%sNew_Itemeditbackground.png" %(sep,sep,sep),
                            extinv=extinv)
    print items,extitems
    surface=itemsurface(items,
                    "..%sdata%sObjekte%sItems%s" %(sep,sep,sep,sep))
    screen=pygame.display.set_mode((800,480))
    #screen.fill((255,255,0))
    screen.blit(surface,(0,0))
    
    pygame.display.update()
    time.sleep(0.5)
    pygame.quit()
