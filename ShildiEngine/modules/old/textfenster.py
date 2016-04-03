# -*- coding: iso-8859-1 -*-
from xturtle import*
import os.path
from time import sleep

# __file__ wird erst beim import definiert
if __name__ == "__main__":
    import textfenster
    meinverzeichnis = os.path.dirname(textfenster.__file__)
else:
    meinverzeichnis = os.path.dirname(__file__)

    
class Textfenster (Turtle):    
    #print meinverzeichnis, __file__
    def __init__(self):
        Turtle.__init__(self)
        self.penup()
        self.goto((0,-222))
        self.addshape(meinverzeichnis+"/redefenster.gif")
        self.shape(meinverzeichnis+"/redefenster.gif")
        self.laufend = False
        self.momentantext = ""

    def erstellschreiber(self):
        if not hasattr(self,"schreiber"):
            self.schreiber = Turtle()
            self.schreiber.hideturtle()
            self.schreiber.rt(90)
            self.schreiber.penup()
            self.schreiber.goto(-150,0)
        
    def neumalen(self):
        self.shape(meinverzeichnis + "/redefenster.gif")
        self.erstellschreiber()

    def rausfahren(self):
        self.goto(0,-45)

    def reinfahren(self):
        self.goto(0,-222)
        
    def reinorausfahren(self, erinnern = False):
        self.erstellschreiber()
        if self.pos() == (0,-222):
            self.goto(0,-45)
            self.schreiber.penup()
            self.schreiber.goto(-150,0)
            if erinnern == True:
                self.schreib("",8,self.momentantext)
        elif self.pos() == (0,-45):
            self.schreiber.clear()
            self.goto(0,-222)
        else:
            self.goto(0,-222)
            
    def schreib(self,text="Nichts los ",groesse=16, zusatztext="",waittime=2,schriftart='Arial'):
        if self.laufend == True:
            return
        self.laufend = True
        self.erstellschreiber()
        self.rausfahren()
        self.momentantext += text
        schreiber = self.schreiber
        schreiber.penup()
        schreibtext = text + str(zusatztext)
        for i in schreibtext:
            if self.schreiber.pos()[0]>160 or i=="\n" or (
                self.schreiber.pos()[0]>100 and (i == " "or i=="-")):
                if i not in ("\n"," "):
                    self.schreiber.write("-", move=True, font=(schriftart, groesse, 'normal'))
                self.schreiber.goto((-150,self.schreiber.pos()[1]-(groesse+3)))
            if self.schreiber.pos()[1]<-120:
                sleep(waittime)
                self.loesch(False)
            schreiber.write( i, move=True, font=(schriftart, groesse, 'normal'))
            sleep(waittime/100.0)
        schreiber.pendown()
        self.laufend = False

    def loesch (self,resetmind=True):
        try:
            self.schreiber.reset()
            self.schreiber.penup()
            self.schreiber.hideturtle()
            self.schreiber.rt(90)
            self.schreiber.goto(-150,0)
        except:
            return None
        if resetmind == True:
            self.momentantext = ""


if __name__ == "__main__":
    def reinorausfahrenohneargumente():
        hi.reinorausfahren(True)
    hi = Textfenster()
    hi.onkey(reinorausfahrenohneargumente,"s")
    hi.onkey(hi.schreib,"w")
    hi.onkey(hi.loesch,"space")
    sleep(3)
    hi.reinorausfahren()
    hi.schreib("Das ist ein sehr "
               "langer Probetext wo\n"
               "ich nicht weiß was\n"
               "ich schreiben soll\n"
               "!!!!!!! !!!!!!!!!!!\n"
               "§§§§-§§§§-§§§§-§§§§§-ðððð-ðððð-ðððð-ðððð-ðjjj-jjjj-jjjj"
               "\n!^`¶\n"
               "øøøøøøøøøøøøøøø")
    hi.listen()
