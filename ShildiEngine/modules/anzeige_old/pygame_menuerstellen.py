# -*- coding: utf-8 -*-
import pygame
import pygame.locals as pgl
import time

def openmenu(liste,screen=None,inform=True,title=None,
             closeafterticking=True,FULLSCREEN=False):
    """liste in Form:z.B.
liste = [("string", func1),
         ("untermenu", [ ("image:imagename","back"),
                         ("string","quit"),
                       ]),
        ]
wenn eine meldung wenn ein Befehl nicht
funktioniert unerwünscht ist :
    inform = False
wenn falsche Befehle einen Fehler egeben sollen:
    inform = "error" """

    # pygame screen erzeugen:
    
    if screen==None:
        pygame.init()
        if FULLSCREEN:
            screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((800, 480))
    if title:
        pygame.display.set_caption(title)
    pygame.mouse.set_visible(True)
    
    listeactiv = liste
    wo = []
    returnvalue = None
    ende = False
    def findstringintupelinlist(liste,string):
        """findet string in liste und gibt position an"""
        for i in range(len(liste)):
            if liste[i][0] == string:
                return i

    def malebuttons(listetmp,y):
        buttondict={}
        font=pygame.font.Font(None, 44)
        screen.fill((50,50,50))
        for (buttontext, buttonfunc),index in listetmp:
            x1, y1 = 20, index*60+y
            x2, y2 = x1+440, y1+50
            buttondict[(x1,y1,x2,y2)]=(buttontext,buttonfunc)
            
            if buttontext[0:6]=="image:":
                image = pygame.image.load(buttontext[6:])
                screen.blit(image,(x1,y1,x2,y2))
            else:
                buttontext = font.render(buttontext, 1,
                                         (255, 255, 255))
                screen.blit(buttontext,(x1,y1,x2,y2))
        pygame.display.update()
        return buttondict
        
    ende = False
    while not ende:
        global pushed
        #print pushed # geht das bevor ein wert zugewiesen ist?
        #             # Ausprobiert:geht nicht
        pushed = (None, "quit") #einstellungen bei Windowdelete

        imagelist=[]
        listetmp =[]
        y=0
        for i in range(len(listeactiv)):listetmp.append((listeactiv[i],i))
        buttonposdict=malebuttons(listetmp,y)
        
        # LOOP
        loopend = False
        mousepos=(400,240)
        while not loopend:
            pygame.display.update()
            # check for events
            events=pygame.event.get()
            for event in events:
                if event.type == pgl.QUIT:
                    beenden=True
                elif event.type == pgl.MOUSEBUTTONUP:
                    print mousepos, event.button, buttonposdict
                    if event.button == 1:
                        for (x1,y1,x2,y2),butpush in buttonposdict.items():
                            if x1<mousepos[0]<x2 and y1<mousepos[1]<y2:
                                pushed = butpush
                                loopend = True

                elif event.type == pgl.MOUSEMOTION:
                    mousepos = event.pos

                elif event.type == pgl.KEYUP:
                    if event.key == pgl.K_ESCAPE:
                        if len(wo)>0:
                            pushed = ("Back","back")
                        else:
                            pushed = ("Quit","quit")
                        loopend = True
            if mousepos[1]<5 and y<0:
                y+=10
                malebuttons(listetmp,y)
                time.sleep(0.05)
            elif mousepos[1]>475:
                y-=10
                malebuttons(listetmp,y)
                time.sleep(0.05)
        
        # AUSWERTUNG DES GEDRÜCKTEN
        
        if str(pushed[1])[0] == "[":
            tmp=findstringintupelinlist(listeactiv, pushed[0])
            wo.append(tmp)
            listeactiv = listeactiv[tmp][1]
            #print listeactiv
        elif str(pushed[1]) == "back":
            wo.pop(-1)
            listeactiv = liste
            for koordinat in wo:
                #print koordinat
                listeactiv = listeactiv[koordinat][1]
        else:
            if closeafterticking == True:
                ende = True
            if inform!="error":
                try:
                    if str(type(pushed[1]))=="<type 'function'>":
                        pushed[1]()
                    elif pushed[1]=="quit":
                        ende = True
                    else:
                        returnvalue=pushed[1]
                except:
                    if inform == True:
                        print "Befehl unbekannt"
            else:
                if str(type(pushed[1]))=="<type 'function'>":
                    pushed[1]()
                elif pushed[1]=="quit":
                    ende = True
                else:
                    returnvalue=pushed[1]
                
    pygame.mouse.set_visible(False)
    return returnvalue

if __name__ == "__main__":

    def sagmirwasneues():     
        print "aha: "+ raw_input("was gibt es neues?")
    dasistkeinbefehl = None
    button1menu = [("zurück","back"),("Befehl",sagmirwasneues)]

    print openmenu([("button1",button1menu),
                  ("falscher\nBefehl",dasistkeinbefehl),
                  ("ruckgabewert","hallo"),
                  ("ende","quit"),
                  #("image:redefenster.gif",sagmirwasneues)
                  ],inform="error",title="hi",
                 closeafterticking=False)
    pygame.quit()
