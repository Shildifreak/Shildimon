# -*- coding: utf-8 -*-
import pygame, ConfigParser
import pygame.locals as pgl
import os, time
import pygame_menuerstellen

sep = os.path.sep

itemdefaults={}

def getdefaults(itemname,itempath):
    if itemname not in itemdefaults:
        configleser = ConfigParser.ConfigParser()
        configleser.read(itempath+itemname+sep+"config.cfg")
        itemdefaults[itemname] = configleser.defaults()
    return itemdefaults[itemname]

def itemmenu(pages,itempath,fullscreen=False):
    print("startet menu")
    pygame.init()
    if fullscreen:
        screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption('Itemmenu')
    pygame.mouse.set_visible(True)
    mainClock = pygame.time.Clock()
    bigitembg = pygame.image.load(itempath+"bg.png")
    reditembg = pygame.image.load(itempath+"bg_red.png")
    editbuttons = pygame.image.load(itempath+"bg_buttons.png")
    leisteunten = pygame.image.load(itempath+"leiste_unten.png")
    leisteoben = pygame.image.load(itempath+"leiste_oben.png")
    leistelinks = pygame.image.load(itempath+"leiste_links.png")
    leisterechts = pygame.image.load(itempath+"leiste_rechts.png")

    mousepos = list(pygame.mouse.get_pos())
    pagepointer = [[]]*len(pages)
    currentitem = [None,None,None] #site,itemplace,item
    infoitem    = None
    currentsites = [i[0] for i in pages]
    viewpos = (0,0)
    shapes={}
    bgimages={}
    textimages={}
    tags={}
    mouseturn=0

    def rotate90(shape):
        return [(y,-x) for (x,y) in shape]

    def getshape(item):
        if item in shapes.keys():
            return shapes[item]
        configleser = ConfigParser.ConfigParser()
        configleser.read(itempath+item[:-1]+sep+"config.cfg")
        shape=configleser.defaults()["shape"]
        if shape.find("|")==-1:
            xd=shape.find("+")
            yd=0
        else:
            xd=int((shape.find("+")+1)%(shape.find("|")+1))-1
            yd=int((shape.find("+")+1)/(shape.find("|")+1))
        shape=shape.split("|")
        shapelist = []
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x] in "x+":
                    shapelist.append((x-xd,y-yd))
        
        rotate=int(item[-1:])
        for i in range(rotate):
            shapelist=rotate90(shapelist)
        shapes[item]=shapelist
        return shapelist
    
    def prepareinventar(item):
        from ast import literal_eval
        configleser = ConfigParser.ConfigParser()
        configleser.read(itempath+item[0][:-1]+sep+"config.cfg")
        if configleser.defaults().has_key("inventar"):
            itemplaces=literal_eval(configleser.defaults()["inventar"])
            for itemplace in itemplaces:
                tags[(item[0][:-1],)+tuple(itemplace[:3])]=list(itemplace[3:])
            for x,y,art in [i[:3] for i in itemplaces]:
                if not item[1].has_key((x,y)):
                    item[1][(x,y,art)]=["None",{}]
                else:
                    item[1][(x,y,art)]=item[1][(x,y)]
                    item[1].pop((x,y))
                    prepareinventar(item[1][(x,y,art)])
            for x,y,art in item[1].keys():
                if art == "s" and not item[1][(x,y,art)][0]in("None","link"):
                    for xd,yd in getshape(item[1][(x,y,art)][0]):
                        if (xd,yd) != (0,0):
                            item[1][(x+xd,y+yd,art)]=["link",(-xd,-yd)]

    for page in pages:
        prepareinventar(page[0])
    
    def replacelink(site,itemplace,item,replace):
        if item[0]=="link" and replace:
            itemplace=itemplace[0]+item[1][0],itemplace[1]+item[1][1],itemplace[2]
            return site, itemplace, site[1][itemplace]
        return site,itemplace,item

    def postoitem(pos,replace=True):
        site=None
        for pagenr in range(len(pages)):
            page = pages[pagenr]
            if 0<pos[0]-page[1][0]<800 and\
               0<pos[1]-page[1][1]<480:
                site=currentsites[pagenr]
                break
        if site==None:
            return [None,None,None]
        x,y = int((pos[0]-page[1][0])/25),int((pos[1]-page[1][1])/25)
        if site[1].has_key((x,y,"s")):
            return  replacelink(site, (x,y,"s"), site[1][(x,y,"s")],replace)
        for xd in range(4):
            for yd in range(4):
                if site[1].has_key((x-xd,y-yd,"b")):
                    return site, (x-xd,y-yd,"b"), site[1][(x-xd,y-yd,"b")]
                if site[1].has_key((x-xd,y-yd,"c")):
                    return site, (x-xd,y-yd,"c"), site[1][(x-xd,y-yd,"c")]
        return [None,None,None] #site, itemplace, item

    def testformergedivbutton():
        site=None
        for pagenr in range(len(pages)):
            page = pages[pagenr]
            if 0<mousepos[0]-page[1][0]<800 and\
               0<mousepos[1]-page[1][1]<480:
                site=currentsites[pagenr]
                break
        if site==None:
            return
        x,y = int((mousepos[0]-page[1][0])/25),int((mousepos[1]-page[1][1])/25)
        for xd in range(4):
            for yd in range(4):
                if site[1].has_key((x-xd,y-yd,"e")):
                        if yd < 2:
                            print "merge"
                            mergeitems(site)
                        else:
                            print "divide"
                            divideitems(site)

    def mergeitems(site):
        edititems=set()
        for x,y,art in site[1].keys():
            if art == "c":
                if site[1][(x,y,art)][1] != {}:
                    for i in site[1][(x,y,art)][1].values():
                        if i != ["None",{}]:
                            return
                if site[1][(x,y,art)][0] != "None":
                    edititems.add(site[1][(x,y,art)][0][:-1])
        if edititems==set():
            return
        configleser = ConfigParser.ConfigParser()
        options=[]
        werkzeug={}
        for ordner in os.listdir(itempath):
            if "." not in ordner:
                configleser.read(itempath+ordner+sep+"config.cfg")
                if configleser.defaults().has_key("tiles"):
                    for tiles in configleser.defaults()["tiles"].split(";"):
                        l = tiles.replace("#","").split(",")
                        if set(l).symmetric_difference(set(edititems))==set():
                            options.append(ordner)
                            werkzeug[ordner]=[i.replace("#","") for i in tiles.split(",") if "#" in i]
        if options==[]:
            return
        menulist=[]
        for item in options:
            menulist.append((item,item))
        item = pygame_menuerstellen.openmenu(menulist,
                                             closeafterticking=True,
                                             screen=screen)
        pygame.mouse.set_visible(True)
        if item==None:
            return
        werkzeug=werkzeug.get(item,[])
        for x,y,art in site[1].keys():
            if art == "c":
                #print site[1][(x,y,art)][0][:-1], werkzeug
                if not site[1][(x,y,art)][0][:-1] in werkzeug:
                    if item == None:
                        site[1][(x,y,art)]=["None",{}]
                    else:
                        site[1][(x,y,art)]=[item+"0",{}]
                        item=None

    def divideitems(site):
        edititems=set()
        freeslots=1
        for x,y,art in site[1].keys():
            if art == "c":
                if site[1][(x,y,art)][1] != {}:
                    for i in site[1][(x,y,art)][1].values():
                        if i != ["None",{}]:
                            return
                if site[1][(x,y,art)][0] != "None":
                    edititems.add(site[1][(x,y,art)][0][:-1])
                else:
                    freeslots+=1
        if len(edititems) != 1:
            return
        else:
            edititem=edititems.pop()
        configleser = ConfigParser.ConfigParser()
        configleser.read(itempath+edititem+sep+"config.cfg")
        if configleser.defaults().has_key("dividetiles"):
            tiles = configleser.defaults()["dividetiles"].split(",")
        else:
            tiles = configleser.defaults()["tiles"].split(",")
        if tiles==[""]:
            return
        for tile in tuple(tiles):
            if "#" in tile:
                tiles.remove(tile)
        if len(tiles)>freeslots:
            return
        for x,y,art in site[1].keys():
            if art == "c":
                if tiles == []:
                    site[1][(x,y,art)]=["None",{}]
                else:
                    site[1][(x,y,art)]=[tiles.pop(0)+"0",{}]
        
    def getbgimage(item):
        if not bgimages.has_key(item):
            try:
                bgimages[item]=pygame.image.load(
                    itempath+item[:-1]+sep+"bgimage.png")
            except:
                bgimages[item]=pygame.Surface((0,0))
        return bgimages[item]

    def gettextimage(text):
        if not textimages.has_key(text):
            font=pygame.font.Font(None,20)
            textimage=font.render(text,1,(255,255,255))
            textimages[text]=(textimage,pygame.transform.rotate(textimage,90))
        return textimages[text]

    def movepage():
        absmousepos=mousepos[0]+viewpos[0],mousepos[1]+viewpos[1]
        d=105
        l=25
        if absmousepos[0]<l or absmousepos[0]>799-l or absmousepos[1]<l or absmousepos[1]>479-l:
            x=int((absmousepos[0]/800.0-0.5)*d*2)
            y=int((absmousepos[1]/480.0-0.5)*d*2)
            return (viewpos[0]-x,viewpos[1]-y),(mousepos[0]+x,mousepos[1]+y),True
        return viewpos,mousepos,False

    def arrangepage():
        nearest=None
        for point in [i[1] for i in pages]:
            d2 = (point[0]-mousepos[0]+480)**2+(point[1]-mousepos[1]+240)**2
            if not nearest:
                nearest=(d2,point)
            elif nearest[0]>d2:
                nearest=(d2,point)
        if abs(viewpos[0]+nearest[1][0])<=1 and\
           abs(viewpos[1]+nearest[1][1])<=1:
            return viewpos, mousepos, False
        m1=(viewpos[0]+nearest[1][0])
        m2=(viewpos[1]+nearest[1][1])
        v=100.
        x=((m1>0)*2-1)*(v-v/(abs(m1)/v+1))
        y=((m2>0)*2-1)*(v-v/(abs(m2)/v+1))
        return (viewpos[0]-x,viewpos[1]-y),(mousepos[0]+x,mousepos[1]+y),True

    def setinfobox(item):
        if item == [None,None,None]:
            return

        if len(item[2])>=3:
            attribute=item[2][2].get("attr",[])
        else:
            attribute=[]

        item = item[2][0]
        if item == "None":
            return
        configleser = ConfigParser.ConfigParser()
        describtion=""
        Configfile=itempath+item[:-1]+sep+"config.cfg"
        configleser.read(Configfile)
        describtion = configleser.defaults()["describtion"]
        adjend = configleser.defaults().get("adjektivendung","")
        numtoword = {1:"fast nicht",2:"wenig",3:"ein bisschen",4:"relativ",5:"ziemlich",6:"fast",7:""}
        attributestr=""
        for i in attribute:
            attributestr+=numtoword[i[1]]+" "+i[0]+adjend+" "
        name = configleser.defaults()["name"]
        image=pygame.image.load(itempath+item[:-1]+sep+"image.png")

        update()
        pygame.draw.rect(screen,(50,50,50),(510,60,500,300))
        screen.blit(image,(520,65))
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
            screen.blit(zeile, textpos)

        screen.blit(font.render(name.decode("utf8"),1,(255,255,255)),(620,120))

        passt=False; height=36; width=150
        for i in range(0,height):
            if not passt:
                size=height-i
                font=pygame.font.Font(None,size)
                if font.size(attributestr.decode("utf8"))[0]<width:
                    passt=True
        screen.blit(font.render(attributestr.decode("utf8"),1,(255,255,255)),(620,80))
        pygame.display.update()
        
    def changeitems():
        zielitemdata = postoitem(mousepos,False)
        if zielitemdata==[None,None,None]:
            return
        site,(x,y,art),zielitem = zielitemdata
        placetags = tags[(site[0][:-1],x,y,art)]
        placetags1 = [tag[1:] for tag in placetags if tag.startswith("#")]
        placetags=[tag.replace("#","") for tag in placetags]
        print "placetags:", placetags, placetags1
        if placetags1!=[]:
            configleser = ConfigParser.ConfigParser()
            configleser.read(itempath+currentitem[2][0][:-1]+sep+"config.cfg")
            itemtags=configleser.defaults().get("tags","").split(",")
            itemtags1=[tag[1:] for tag in itemtags if tag.startswith("#")]
            itemtags=[tag.replace("#","") for tag in itemtags]
            print "itemtags:", itemtags,itemtags1
            if not set(placetags1).issubset(set(itemtags)):
                return
            if not set(itemtags1).issubset(set(placetags)):
                return
        if art in "bc":
            if zielitem[0]=="None":
                clearcurrentitem()
                site[1][(x,y,art)]=currentitem[2]
        elif art=="s":
            free = set([key for key,value in site[1].items() if\
                        value == ["None",{}] or value is currentitem[2] or\
                       ((value[0] == "link") and (site[1][key[0]+value[1][0],key[1]+value[1][1],art] is currentitem[2]))])
            new  = set([(x+xd,y+yd,"s") for xd,yd in getshape(currentitem[2][0][:-1]+str(mouseturn))])
            if new.issubset(free):
                #HIER TAGPRÜFEN FÜR ALLE FELDER EINFÜGEN
                clearcurrentitem()
                currentitem[2][0]=currentitem[2][0][:-1]+str(mouseturn)
                site[1][(x,y,art)]=currentitem[2]
                for xd,yd in getshape(currentitem[2][0]):
                    if (xd,yd) != (0,0):
                        site[1][(x+xd,y+yd,art)]=["link",(-xd,-yd)]
    
    def clearcurrentitem():
        if currentitem[1][2] in "bc":
            currentitem[0][1][currentitem[1]]=["None",{}]
        else:
            x,y,art = currentitem[1]
            for xd,yd in getshape(currentitem[2][0]):
                currentitem[0][1][x+xd,y+yd,art]=["None",{}]

    def goup():
        for pagenumber in range(len(pages)):
            page = pages[pagenumber]
            if 0<mousepos[0]-page[1][0]<800 and\
               0<mousepos[1]-page[1][1]<480:
                site=page[0]
                break
        if len(pagepointer[pagenumber])==0:
            return True #beenden
        pagepointer[pagenumber].pop(-1)
        for i in pagepointer[pagenumber]:
            site = site[1][i]
        currentsites[pagenumber] = site
        update()
        return False

    def godown():
        site,itemplace,item = postoitem(mousepos)
        if (itemplace != None) and (item[0] not in "link","None") and item[1]!={} and item!=currentitem[2]:
            pagenumber = currentsites.index(site)
            pagepointer[pagenumber].append(itemplace)
            currentsites[pagenumber] = item
        update()
        
    
    def update(x1=0,y1=0,x2=800,y2=480):
        screen.fill((0,0,0))
        for pagenumber in range(len(pages)):
            #print "pagenumber:",pagenumber, currentsites[pagenumber][1].values()
            pagepos=pages[pagenumber][1]
            screen.blit(getbgimage(currentsites[pagenumber][0]),
                        (pagepos[0]+viewpos[0],pagepos[1]+viewpos[1]))
            deko=int(getdefaults(currentsites[pagenumber][0][:-1],itempath).get("deko",1))
            for x,y,art in currentsites[pagenumber][1].keys():
                if art == "s" and deko:
                    pygame.draw.rect(screen,(100,100,100),
                                 (25*x+pagepos[0]+viewpos[0],
                                  25*y+pagepos[1]+viewpos[1],25,25))
                elif art == "b" and deko:
                    screen.blit(bigitembg,(25*x-15+viewpos[0]+pagepos[0],25*y-15+viewpos[1]+pagepos[1]))
                elif art == "c" and deko:
                    screen.blit(reditembg,(25*x-15+viewpos[0]+pagepos[0],25*y-15+viewpos[1]+pagepos[1]))                    
                elif art == "e" and deko:
                    screen.blit(editbuttons,(25*x-15+viewpos[0]+pagepos[0],25*y-15+viewpos[1]+pagepos[1]))                    
            for x,y,art in currentsites[pagenumber][1].keys():
                item=currentsites[pagenumber][1][x,y,art][0]
                if (not item in ("None","link")) and (not\
                   currentsites[pagenumber][1][x,y,art] is currentitem[2]):
                    if art in "bc":
                        screen.blit(
                        pygame.image.load(itempath+item[:-1]+sep+"image.png"),(25*x+pagepos[0]+viewpos[0],25*y+pagepos[1]+viewpos[1]))
                    elif art == "s":
                        shape=getshape(item)
                        xd=min([i[0] for i in shapes[item]])
                        yd=min([i[1] for i in shapes[item]])
                        rotate=int(item[-1:])*90
                        screen.blit(
                            pygame.transform.rotate(
                            pygame.image.load(itempath+item[:-1]+sep+"shape.png"),
                            rotate),
                            (25*(x+xd)+pagepos[0]+viewpos[0],25*(y+yd)+pagepos[1]+viewpos[1]))
        for pagenumber in range(len(pages)):
            pagepos=pages[pagenumber][1]
            screen.blit(leisteoben,(pagepos[0]+viewpos[0],pagepos[1]+viewpos[1]+482))
            screen.blit(leisteunten,(pagepos[0]+viewpos[0],pagepos[1]+viewpos[1]-27))
            screen.blit(leistelinks,(pagepos[0]+viewpos[0]+802,pagepos[1]+viewpos[1]))
            screen.blit(leisterechts,(pagepos[0]+viewpos[0]-27,pagepos[1]+viewpos[1]))
            textimg1,textimg2=gettextimage(currentsites[pagenumber][0][:-1])
            x=textimg1.get_width()/2
            screen.blit(textimg1,(pagepos[0]+viewpos[0]+400-x,pagepos[1]+viewpos[1]+482))
            screen.blit(textimg1,(pagepos[0]+viewpos[0]+400-x,pagepos[1]+viewpos[1]-23))
            screen.blit(textimg2,(pagepos[0]+viewpos[0]+802,pagepos[1]+viewpos[1]+240-x))
            screen.blit(textimg2,(pagepos[0]+viewpos[0]-23,pagepos[1]+viewpos[1]+240-x))
    update()
    # LOOP
    print("start loop")
    end = False
    mleft, mright, mup, mdown = 0,0,0,0
    kmleft = pgl.K_LEFT;kmright = pgl.K_RIGHT;kmup = pgl.K_UP;kmdown = pgl.K_DOWN
    kleft = pgl.K_a;kright = pgl.K_d;kscrollup = pgl.K_w;kscrolldown =pgl.K_s
    pygame.event.get()
    while not end:
        mainClock.tick(16)
        # check for events
        events=pygame.event.get()
        for event in events:
            if event.type == pgl.QUIT: end=True
            #TASTATUR
            if event.type == pgl.KEYDOWN:
                if event.key in (pgl.K_TAB,pgl.K_ESCAPE):
                    end=True
                if event.key == kmright: mright=0.5
                elif event.key == kmleft: mleft=0.5
                elif event.key == kmup:     mup=0.5
                elif event.key == kmdown: mdown=0.5
                if event.key == kleft:
                    currentitem = postoitem(mousepos)
                    if currentitem!=[None,None,None] and\
                       currentitem[2][0]=="None":
                        currentitem=[None,None,None]
                    if currentitem!=[None,None,None]:
                        mouseturn=int(currentitem[2][0][-1])
                    if currentitem==[None,None,None]:
                        testformergedivbutton()
                    update()
                    pygame.display.update()
                    #print mode
                if event.key == kright and currentitem!=[None,None,None]:
                    mouseturn=(mouseturn+1)%4
                if event.key == kright and currentitem==[None,None,None]:
                    infoitem = postoitem(mousepos)
                else:
                    infoitem = None
                if event.key == kscrollup:
                    godown()
                if event.key == kscrolldown:
                    end = goup()
            if event.type == pgl.KEYUP:
                if event.key == kmright: mright=0
                elif event.key == kmleft: mleft=0
                elif event.key == kmup:     mup=0
                elif event.key == kmdown: mdown=0
                elif event.key == kleft:
                    if currentitem != [None,None,None]:
                        changeitems()
                    currentitem = [None,None,None]
                    update()
            #MAUS
            if event.type == pgl.MOUSEBUTTONDOWN:
                if event.button == 1:
                    currentitem = postoitem(mousepos)
                    if currentitem!=[None,None,None] and\
                       currentitem[2][0]=="None":
                        currentitem=[None,None,None]
                    if currentitem!=[None,None,None]:
                        mouseturn=int(currentitem[2][0][-1])
                    if currentitem==[None,None,None]:
                        testformergedivbutton()
                    update()
                    pygame.display.update()
                    #print mode
                if event.button == 3 and currentitem!=[None,None,None]:
                    mouseturn=(mouseturn+1)%4
                if event.button == 3 and currentitem==[None,None,None]:
                    infoitem = postoitem(mousepos)
                else:
                    infoitem = None
                if event.button == 4:
                    godown()
                if event.button == 5:
                    end = goup()
            if event.type == pgl.MOUSEBUTTONUP:
                if event.button == 1:
                    if currentitem != [None,None,None]:
                        changeitems()
                    currentitem = [None,None,None]
                    update()
            if event.type == pgl.MOUSEMOTION:
                mousepos = [event.pos[0]-viewpos[0],event.pos[1]-viewpos[1]]
            else:
                pygame.mouse.set_pos([mousepos[0]+viewpos[0],mousepos[1]+viewpos[1]])
                
        mousemotion = [int(mright)-int(mleft),int(mdown)-int(mup)]
        if abs(mright-mleft)==0.5:
            mousemotion[0]=(mright>mleft)*2-1
        if abs(mdown-mup)==0.5:
            mousemotion[1]=(mdown>mup)*2-1
        mousepos = list(mousepos)
        xpos = int((mousepos[0]+viewpos[0])/25+mousemotion[0])*25+13
        ypos = int((mousepos[1]+viewpos[1])/25+mousemotion[1])*25+13
        a=1.2
        if 0<=xpos<=800:
            if mousemotion[0]!=0:
                mousepos[0]=xpos-viewpos[0]
                pygame.mouse.set_pos([mousepos[0]+viewpos[0],mousepos[1]+viewpos[1]])
        else:a=0.5
            #M#
        if 0<=ypos<=480:
            if mousemotion[1]!=0:
                mousepos[1]=ypos-viewpos[1]
                #print ypos,mousemotion[1],viewpos[1],mdown,int(viewpos[1]+13.5)%25
                pygame.mouse.set_pos([mousepos[0]+viewpos[0],mousepos[1]+viewpos[1]])
        else:a=0.5
        mright*=a; mleft*=a; mup*=a; mdown*=a
        if currentitem == [None,None,None]:
            for page in pages:
                itemattrupdate(page[0],itempath)

        viewpos,mousepos,chbool1=movepage()
        viewpos,mousepos,chbool2=arrangepage()

        if infoitem:
            setinfobox(infoitem)

        if chbool1 or chbool2:
            update()
        
        if currentitem!=[None,None,None]:
            mouseitem=currentitem[2][0][:-1]+str(mouseturn)
            if postoitem(mousepos)[1] != None and\
               postoitem(mousepos)[1][2]=="s":
                imagesort="shape.png"
            else:
                imagesort="image.png"
            if imagesort=="shape.png":
                xd=min([i[0] for i in getshape(mouseitem)])
                yd=min([i[1] for i in getshape(mouseitem)])
                #print (shape.find("+")+1),(shape.find("|")+1),x,y
                imagepos=(mousepos[0]+25*xd+viewpos[0]-13,
                          mousepos[1]+25*yd+viewpos[1]-13)
                rotate=int(mouseturn)*90
            else:
                imagepos=(mousepos[0]-50+viewpos[0],
                          mousepos[1]-50+viewpos[1])
                rotate=0
            update()
            screen.blit(
                pygame.transform.rotate(
                    pygame.image.load(itempath+mouseitem[:-1]
                                    +sep+imagesort),rotate)
                ,imagepos)
        pygame.display.update()

    
    def clearinventar(item):
        if item[1]!={}:
            for x,y,art in item[1].keys():
                if not item[1][(x,y,art)][0] in ("None","link"):
                    clearinventar(item[1][(x,y,art)])
                    item[1][(x,y)]=item[1][(x,y,art)]
                item[1].pop((x,y,art))

    for page in pages:
        clearinventar(page[0])

    return pages

def itemattrupdate(item,itempath):
    from ast import literal_eval
    configleser = ConfigParser.ConfigParser()
    configleser.read(itempath+item[0][:-1]+sep+"config.cfg")
    attrchange=configleser.defaults().get("attrchange",None)
    for contentitem in item[1].values():
        if not contentitem[0] in ("link","None"):
            itemattrupdate(contentitem,itempath)
            """
            configleser = ConfigParser.ConfigParser()
            configleser.read(itempath+contentitem[0][:-1]+sep+"config.cfg")
            attrchangen=configleser.defaults().get("attrchangen",None)
            for contentitem2 in item[1].values():
                if not contentitem2[0] in ("link","None"):
                    if attrchangen!=None:
                        attrchnlist=literal_eval(attrchangen)
                        for aktion in attrchnlist:
                            if aktion.startswith("+"):
                                if len(contentitem2)<3:
                                    contentitem2.append({})
                                if not contentitem2[2].has_key("attr"):
                                    contentitem2[2]["attr"]=[]
                                erledigt=False
                                for attr in contentitem2[2]["attr"]:
                                    if attr[0] == aktion[1:]:
                                        attr[1]+=1
                                        if attr[1]>7:
                                            attr[1]=7
                                        erledigt = True
                                if not erledigt:
                                    contentitem2[2]["attr"].append([aktion[1:],1])
                            if aktion.startswith("-"):
                                if len(contentitem2)<3:
                                    pass
                                elif not contentitem2[2].has_key("attr"):
                                    pass
                                else:
                                    for attrnum in range(len(contentitem2[2]["attr"])):
                                        attr = contentitem2[2]["attr"][attrnum]
                                        if attr[0] == aktion[1:]:
                                            attr[1]-=1
                                            if attr[1]==0:
                                                contentitem2[2]["attr"][attrnum]=None
                                    while None in contentitem2[2]["attr"]:
                                        contentitem2[2]["attr"].remove(None)
    """
    if attrchange!=None:
        attrchlist=literal_eval(attrchange)
        if len(item)==2:
            item.append({})
        if len(item[2].get("attrch",[]))<len(attrchlist):
            item[2]["attrch"]=[time.time()]*len(attrchlist)
        for attrchnum in range(len(attrchlist)):
            attrch = attrchlist[attrchnum]
            delay = attrch[0]
            if time.time()-item[2]["attrch"][attrchnum]>delay:
                item[2]["attrch"][attrchnum]=time.time()
                for contentitem in item[1].values():
                    if not contentitem[0] in ("link","None"):
                        allbedingung=True
                        for bedingung in attrch[1:]:
                            if bedingung[0] in ".:":
                                vergleichitem = item
                            else:
                                vergleichitem = contentitem
                            if bedingung[0] in "#.":
                                if len(contentitem)<3:
                                    allbedingung=False
                                elif not (bedingung[1:] in [i[0] for i in vergleichitem[2].get("attr",[])]):
                                    allbedingung=False                                    
                            if bedingung[0] in "!:":
                                if not len(contentitem)<3:
                                    if (bedingung[1:] in [i[0] for i in vergleichitem[2].get("attr",[])]):
                                        allbedingung=False
                        if allbedingung:
                            for aktion in attrch[1:]:
                                if aktion.startswith("+"):
                                    if len(contentitem)<3:
                                        contentitem.append({})
                                    if not contentitem[2].has_key("attr"):
                                        contentitem[2]["attr"]=[]
                                    erledigt=False
                                    for attr in contentitem[2]["attr"]:
                                        if attr[0] == aktion[1:]:
                                            attr[1]+=1
                                            if attr[1]>7:
                                                attr[1]=7
                                            erledigt = True
                                    if not erledigt:
                                        contentitem[2]["attr"].append([aktion[1:],1])
                                if aktion.startswith("-"):
                                    if len(contentitem)<3:
                                        pass
                                    elif not contentitem[2].has_key("attr"):
                                        pass
                                    else:
                                        for attrnum in range(len(contentitem[2]["attr"])):
                                            attr = contentitem[2]["attr"][attrnum]
                                            if attr[0] == aktion[1:]:
                                                attr[1]-=1
                                                if attr[1]==0:
                                                    contentitem[2]["attr"][attrnum]=None
                                        while None in contentitem[2]["attr"]:
                                            contentitem[2]["attr"].remove(None)

def itemsurface(items,itemimgspath):
    pygame.init()
    background = pygame.Surface((800,130))
    background = background.convert_alpha()
    background.fill((0,0,0,0))
    iteml=items.get((15,12),["None"])[0]
    itemr=items.get((23,12),["None"])[0]
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

if __name__ == "__main__":
    # s: kleines Feld, b: großes Feld, c: crafting, e: craften ausführen
    player=["Player0",{}]
    player[1][(6,2)]=["Magnetangel0",{}]
    player[1][(19,5)]=["Rucksack0",{}]
    #player[1][(6,6)]=["Flasche0",{(10,10):["Beere1",{}]}]
    #player[1][(16,10,"e")]=["Hand",{}]
    crafting = None #[tag,buttonpos,listof_b_fields]
    pagepos = (0,0)
    page1 = [player,pagepos]
#    truhe=["Ofen0",{}]
    truhe=["Truhe0",{}]
    truhe[1][(17,7)]=["Beere0",{},{"attr":[["nass",7]]}]
    truhe[1][(13,7)]=["Topf0",{},{"attr":[["feuerresistent",7]]}]
    #truhe[1][(14,8)]=["Wasser1",{},{"attr":[["feuerresistent",7]]}]
    #player2[1][(16,10,"e")]=["Hand",{}]
    stein=["Experimentiertisch0",{(1,1):["Schale0",{}],
                                  (7,1):["Uraninit0",{}],
                                  (13,1):["Tiegelzange0",{}],
                                  (1,7):["Salzsaeure0",{}],
                                  (7,7):["Flasche0",{}],
                                  (13,7):["Geigerzaehler0",{}]}]
    stein2=["Montagestein0",{}]
    #page2 = [truhe,(0,-480)]
    #page2 = [stein,(100,-480)]
    #page2 = [stein2,(0,-480)]
    page2 = [stein2,(800,0)]
    pages = [page1,page2]
    itemimgspath = "..%sdata%sObjekte%sItems%s" %(sep,sep,sep,sep)
    pages = itemmenu(pages,itemimgspath,fullscreen=False)
    print pages
    surface=itemsurface(pages[0][0][1],
                    "..%sdata%sObjekte%sItems%s" %(sep,sep,sep,sep))
    screen=pygame.display.set_mode((800,480))
    #screen.fill((255,255,0))
    screen.blit(surface,(0,0))
    pygame.display.update()
    time.sleep(0.5)
    pygame.quit()
