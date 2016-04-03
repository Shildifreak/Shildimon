# -*- coding: utf-8 -*-
import pygame
import os,math,time

SUPPORTS_3D_UPDATE = False
ShildiEngineIOlibIndicator = None #Wert ist egal, muss nur vorhanden sein

def nested_split(string,sep=",",incchar="(",decchar=")",stringchar='"'):
    sep = ",-" #M#
    nesting_level = 0
    isstring = False
    results = [""]
    for buchstabe in string:
        if (buchstabe in sep) and (nesting_level == 0) and not isstring:
            results.append("")
        else:
            if buchstabe == incchar and not isstring:
                nesting_level += 1
            elif buchstabe == decchar and not isstring:
                nesting_level -= 1
            elif buchstabe == stringchar:
                isstring = not isstring
            results[-1]+=buchstabe
    return results

class Display():
    def __init__(self,datapath,displaycfg={}):
        #pygame.init()
        pygame.display.init()
        pygame.font.init()
        #pygame.joystick.init()

        self.displaycfg = displaycfg
        self.datapath = datapath
        self.defaultfont = os.path.join(datapath,"Fonts","Artifika.ttf")

        self.window = pygame.display.get_surface()
        if not self.window:
            self.width = int(self.displaycfg.get("width",0))
            self.height = int(self.displaycfg.get("height",0))
            self.window = pygame.display.set_mode((self.width,self.height),
                                                  pygame.RESIZABLE)
        self.width,self.height = self.window.get_size()

        self.old_images = [] #(name,pos,size)
        self.new_images = [] #(name,pos,size)
        self.cleared = True
        self.focus = [] #images at pointer and pos of pointer on image

        self.mousepos = pygame.mouse.get_pos()

        self.imagepaths = {}
        self.images = {}
        self.scaled_images = {}
        self.combistoremin = self.displaycfg.get("combistoremin",0) # <- increasing integer uses less memory, but needs more calculation time
        self.UPDATETYPEDEFAULT = "all" # of "all"(default), ["onchange", "difference"]
        self.UPDATETYPE = self.displaycfg.get("updatetype","auto")
        if self.UPDATETYPE == "auto":
            self.UPDATETYPE = self.UPDATETYPEDEFAULT
        self.fontscales = {}
        self.fontcache = {}

        os.path.walk(os.path.join(datapath,"Images"),self.add_imagepaths,None)


    def add_imagepaths(self,args,dirname,fnames): #args is necessary for use with walk
        for filename in fnames:
            imagepath = os.path.join(dirname,filename)
            if not os.path.isdir(imagepath):
                self.imagepaths[filename] = imagepath

    def get_mousepos(self):
        return self.mousepos #pygame.mouse.get_pos()

    def get_image_size(self,imagename,size):
        return self.get_image(imagename,size).get_size()

    def get_window_size(self):
        return self.width, self.height

    def update(self,new_images):
        """images in form (imagename,pos,size[,...])"""
        if self.UPDATETYPE in ("all","onchange"):
            blit_new_images = True
            if self.cleared:
                if (self.UPDATETYPE) != "all" and (self.old_images == new_images):
                    blit_new_images = False
                else:
                    self.window.fill((255,255,255))
                self.cleared = False
            for new_image in new_images:
                image_name,pos,size = new_image[:3]
                image = self.get_image(image_name,size)
                if image:
                    if blit_new_images:
                        self.window.blit(image,pos)
                    size = image.get_size()
                    if pos[0]<self.mousepos[0]<pos[0]+size[0] and\
                        pos[1]<self.mousepos[1]<pos[1]+size[1]:
                        self.focus.append((new_image,
                                           (float(self.mousepos[0]-pos[0])/size[0],
                                            float(self.mousepos[1]-pos[0])/size[0])))

            self.old_images = new_images
            #M# if self.blit_new_images: or if display changed size, etc
            pygame.display.update()

            return self.focus
        elif self.UPDATETYPE == "difference":
            update_rects = set([])
            new_images2 = []
            for new_image in new_images:
                image_name,pos,size = new_image[:3]
                image = self.get_image(image_name,size)
                size = image.get_size()
                rect = tuple(pos)+tuple(size)
                if new_image not in self.old_images:
                    update_rects.add(rect)
                    new_images2.append([image,rect+(0,0),True])
                else:
                    new_images2.append([image,rect+(0,0),False])
                if pos[0]<self.mousepos[0]<pos[0]+size[0] and\
                    pos[1]<self.mousepos[1]<pos[1]+size[1]:
                    self.focus.append((new_image,
                                        (float(self.mousepos[0]-pos[0])/size[0],
                                        float(self.mousepos[1]-pos[0])/size[0])))
            for old_image in self.old_images:
                image_name,pos,size = old_image[:3]
                size = self.get_image_size(image_name,size)
                rect = tuple(pos)+tuple(size)
                if old_image not in new_images:
                    update_rects.add(rect)
                    pygame.draw.rect(self.window,(255,255,255),rect)
            for image,rect,changed in new_images2:
                if changed:
                    self.window.blit(image,rect[:2])
                else:
                    x,y,w,h,dummi,dummi = rect
                    for x2,y2,w2,h2 in update_rects:
                        x3 = max(x,x2)
                        y3 = max(y,y2)
                        w3 = min(x+w,x2+w2)-x3
                        h3 = min(y+w,y2+w2)-y3
                        if w>0 and h>0:
                            #self.window.blit(image,(x,y),(0,0,w3,h3))
                            self.window.blit(image,(x3,y3),(x3-x,y3-y,w3,h3))
            self.old_images = new_images
            pygame.display.update(list(update_rects))
            return self.focus
        else:
            print "updatetype",self.UPDATETYPE,"not avaible"
            print "changing updatetype to",self.UPDATETYPEDEFAULT,"(default)"
        
    def clear(self):
        self.focus = []
        self.cleared = True

    def clear_cache(self):
        self.images = {}
        self.scaled_images = {}

    def scale_image(self,image,size):
        """size is tupel (width,height) where width xor height can be None in order to keep ratio"""
        w,h = size
        if image == None:
            return
        if h == None:
            h = 1.0*image.get_height()*w/image.get_width()
        if w == None:
            w = 1.0*image.get_width()*h/image.get_height()
        if image.get_size() == (w,h):
            return image
        return pygame.transform.scale(image,(int(math.ceil(w)),
                                             int(math.ceil(h))))

    def get_font(self,fontname,size):
        font = self.fontcache.get((fontname,size),None)
        if font == None:
            if fontname == None:
                fontname = self.defaultfont
            font = pygame.font.Font(fontname,size)
            self.fontcache[(fontname,size)] = font
        return font

    def get_image(self,imagename,size):
        if size == (None,None):
            print "Error loading %s: size can't be (None,None)" %imagename
            return
        #if not None in (h,w):
        #image = pygame.transform.scale(image,(int(math.ceil(h)),int(math.ceil(w))))
        size2,scaled_image = self.scaled_images.get(imagename,(None,None))
        if size == size2 and scaled_image != None:
            return scaled_image
        elif self.images.has_key(imagename):
            scaled_image = self.scale_image(self.images[imagename],size)
            self.scaled_images[imagename] = (size,scaled_image)
            return scaled_image
        else:
            layernames = nested_split(imagename,",","<",">")
            if len(layernames)!=1:
                tmp = False
                if layernames[0] == "#tmp":
                    layernames.pop(0)
                    tmp = True
                layers = [self.get_image(layername,size) for layername in layernames]
                image = pygame.Surface((max([img.get_width() for img in layers]),
                                        max([img.get_height() for img in layers])))
                for layer in layers:
                    image.blit(layer,(0,image.get_height()-layer.get_height()))
                if self.combistoremin and len(layernames)<self.combistoremin:
                    return self.scale_image(image,size)
                elif tmp:
                    return self.scale_image(image,size)
                else:
                    self.images[imagename] = image
                    return self.scale_image(image,size)
            elif imagename.endswith(">"):
                parameter = nested_split(imagename[1:-1],",","<",">")
                if parameter[0] == "line":
                    xmax,x1,y1,x2,y2,r,g,b,linewidth = [int(float(i)) for i in parameter[1:]]
                    ymax = max(y1,y2)+1
                    image = pygame.Surface((xmax,ymax)).convert_alpha()
                    image.fill((0,0,0,0))
                    pygame.draw.line(image,(r,g,b),(x1,ymax-y1),(x2,ymax-y2),linewidth)
                elif parameter[0] == "text":
                    text = parameter[1].replace('""','"')
                    if text.startswith('"'):
                        text = text[1:]
                    if text.endswith('"'):
                        text = text[:-1]
                    if text != "":
                        r,g,b,a = [int(float(i)) for i in parameter[2:]]
                        color = (r,g,b,a)
                        if a == 0:
                            color = (0,0,0,255)
                            text = "*"*len(text)
                        fontname = None
                        width,height = size
                        #test font scaling including dpi etc:
                        y_factor = self.fontscales.get(fontname,None)
                        if y_factor== None:
                            testfont = self.get_font(fontname,1000)
                            y_factor = 1000./testfont.get_height()
                            self.fontscales[fontname] = y_factor
                        if not width:
                            s = int(y_factor*height)
                        else:
                            testfont = self.get_font(fontname,1000)
                            x_factor = 1000./testfont.size(text)[0]
                            if not height:
                                s = int(x_factor*width)
                            else:
                                s = int(min(x_factor*width,y_factor*height))
                        font = self.get_font(fontname,s)
                        textimg = font.render(text,True,color)
                        if width and height:
                            image = pygame.Surface((width,height)).convert_alpha()
                            image.fill((0,0,0,0))
                            image.blit(textimg,(int((width-textimg.get_width())/2),
                                                int((height-textimg.get_height())/2)))
                        else:
                            image = textimg
                    else:
                        image = pygame.Surface((1,1)).convert_alpha()
                        image.fill((0,0,0,0))
                else:
                    image = pygame.Surface((2,2))
                    image.set_at((0,0),(255,0,255))
                    image.set_at((1,1),(255,0,255))
                #self.images[imagename] = image #M#
                return self.scale_image(image,size)
            elif imagename == "":
                return
            else:
                imagepath = self.imagepaths.get(imagename,None)
                if imagepath == None:
                    imagepath = os.path.join(self.datapath,*imagename.split("/"))
                self.images[imagename] = pygame.image.load(imagepath)
                return self.scale_image(self.images[imagename],size)

    def get_events(self):
        raw_events = []
        events = []
        pygame_events = pygame.event.get()

        # touchscreen compatibility
        pos = None
        for pygame_event in pygame_events[::-1]:
            if pygame_event.type == pygame.MOUSEMOTION:
                pos = pygame_event.pos
            if pygame_event.type == pygame.MOUSEBUTTONDOWN and\
               pygame_event.button == 1:
                if not pos:
                    pos = pygame_event.pos
                pygame_events.remove(pygame_event)
                pygame_events.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                     {"button":pygame_event.button,"pos":pos}))

        newsize = None
        for pygame_event in pygame_events:
            controlkey = None #M#
            if pygame_event.type == pygame.QUIT:
                events.append(("QUIT",None))
            if pygame_event.type == pygame.VIDEORESIZE:
                newsize = pygame_event.size
            if pygame_event.type == pygame.KEYDOWN:
                if pygame_event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                keyname = pygame.key.name(pygame_event.key)
                raw_events.append(("key_"+keyname,1))
                events.append(("character",pygame_event.unicode))
            if pygame_event.type == pygame.KEYUP:
                keyname = pygame.key.name(pygame_event.key)
                raw_events.append(("key_"+keyname,0))
            if pygame_event.type == pygame.MOUSEBUTTONDOWN:
                raw_events.append(("mouse_"+str(pygame_event.button),1))
            if pygame_event.type == pygame.MOUSEBUTTONUP:
                raw_events.append(("mouse_"+str(pygame_event.button),0))
            if pygame_event.type == pygame.MOUSEMOTION:
                self.mousepos = pygame_event.pos
            #M# if pygame_event.type JOYBUTTON JOYHAT JOYSTICK...
        if newsize!=None:
            self.clear_cache()
            windowtmp = self.window.copy()
            self.window = pygame.display.set_mode(newsize,pygame.RESIZABLE)
            self.width,self.height = self.window.get_size()
            windowtmp = pygame.transform.scale(windowtmp,(self.width,self.height))
            self.window.blit(windowtmp,(0,0))
            self.old_images = []
        return raw_events,events

    def set_caption(self,title):
        pygame.display.set_caption(title)

    def close(self):
        pygame.display.quit()

    # UNUSED METHODS:

    def substract_rect(self,(x1,y1,w1,h1,dx1,dy1),(x2,y2,w2,h2,dx2,dy2)):
        result_rects = set([])
        for x,y,w,h,dx,dy in [
                (   x1,   y1,      x2-x1,   y2+w2-y1,       0,       0),
                (   x2,   y1,   x1+w1-x2,      y2-y1,   x2-x1,       0),
                (x2+w2,   y2,x1+w1-x2-w2,   y1+h1-y2,x2+w2-x1,   y2-y1),
                (   x1,y2+h2,   x2+w2-x1,y1+h1-y2-h2,       0,y2+h2-y1)]:
            w = min(w,w1);h = min(h,h1);x = max(x,x1);y = max(y,y1)
            dx+=dx1;dy+=dy1
            if w>0 and h>0:
                result_rects.add((x,y,w,h,dx,dy))
        return result_rects

    def move_old_images(self,dx,dy):
        try:
            window.move(dx,dy)
        except:
            window.blit(window,(dx,dy))
        #...


if __name__ == "__main__":
    d = Display("../data/commondata")
    c = pygame.time.Clock()
    d.set_caption("pygameIO-Test")
    events = []
    while not ("QUIT",None) in events:
        raw_events,events = d.get_events()
        images = [("gras.png",(100,400),(200,None)),
                  ("Images/Menu/default/top.png",(0,0),(None,50)),
                  ("<text,Test,0,0,255,255>",(100,400),(200,200)),
                  ]
        d.update(images)
        c.tick(16)
    d.close()
