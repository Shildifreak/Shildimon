# -*- coding: utf-8 -*-
from Tkinter import*

def openmenu(liste,inform=True,wohin=None,title=None,
             imagestandartsize=None,closeafterticking=True):
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
    inform = "error"
    wohin in Form:"widthxheight+x+y" """
    listeactiv = liste
    wo = []
    ende = False
    def findstringintupelinlist(liste,string):
        """findet string in liste und gibt position an"""
        for i in range(len(liste)):
            if liste[i][0] == string:
                return i
    
    while ende == False:
        root = Tk()
        root.geometry(wohin)
        root.wm_title(title)
        global pushed
        #print pushed # geht das bevor ein wert zugewiesen ist?
        #             # Ausprobiert:geht nicht
        pushed = (None, "quit") #einstellungen bei Windowdelete

        ## Canvas
        cnv = Canvas(root,height=wohin.split("x")[1].split("+")[0],
                     width=wohin.split("x")[0],)
        cnv.grid(row=0, column=1, sticky='nswe')
        ## Scrollbars for canvas
        vScroll = Scrollbar(root, orient=VERTICAL, command=cnv.yview)
        vScroll.grid(row=0, column=0, sticky='ns')
        cnv.configure(yscrollcommand=vScroll.set)
        ## Frame in canvas, and in the canvas's scrollable zone
        frm = Frame(cnv)
        cnv.create_window(0, 0, window=frm, anchor='nw')

        imagelist=[]
        listetmp =[]
        for i in range(len(listeactiv)):listetmp.append((listeactiv[i],i))
        for (buttontext, buttonfun),index in listetmp:
            def _opt(_t=buttontext, _f=buttonfun):
                global pushed
                pushed = (_t, _f)
                #print _t, _f, pushed
                root.quit()

            imagelist.append("")
            if buttontext[0:6]=="image:":
                if buttontext[-4:]==".gif":
                    imagelist[-1] = PhotoImage(file=buttontext[6:],
                                               master=frm)
                else:
                    import PIL.Image, PIL.ImageTk
                    bild = PIL.Image.open(fp=buttontext[6:])
                    if imagestandartsize != None:
                        bild=bild.resize(imagestandartsize)
                    tkbild = PIL.ImageTk.PhotoImage(bild,master=root)
                    imagelist[-1] = tkbild
                
                buttontext  = ""
            b = Button(frm, text = buttontext, command = _opt,
                   image = imagelist[-1],)
            b.pack(anchor=W)
            #b.bind("<Up>",lambda i=index:)
        frm.update_idletasks()
        cnv.configure(scrollregion=(0, 0, frm.winfo_width(), frm.winfo_height()))

        root.protocol("WM_DELETE_WINDOW",root.quit)
        root.mainloop(0)
        #wenn ein Knopf gedrückt wurde
        root.destroy()
        
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
            try:
                if pushed[1]!="quit" and pushed[1]!=None:
                    pushed[1]()
                elif pushed[1]=="quit":
                    ende = True
            except:
                if inform == True:
                    print "Befehl unbekannt"
                elif inform == "error":
                    raise "Befehl: unbekannter Befehl: "+repr(pushed[1])



if __name__ == "__main__":   # wenn menuerstellen importiert wird, 
                             # wird folgendes nicht ausgeführt:
    def sagmirwasneues():     
        print "aha: "+ raw_input("was gibt es neues?")
    dasistkeinbefehl = None
    button1menu = [("zurück","back"),("Befehl",sagmirwasneues)]
    openmenu([("button1",button1menu),
              ("falscher\nBefehl",dasistkeinbefehl),
              ("ende","quit"),
              ("image:redefenster.gif",sagmirwasneues)
              ],inform="error",title="hi",wohin="420x200+0+0",
             closeafterticking=False)
