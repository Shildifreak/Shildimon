# -*- coding: utf-8 -*-
import pygame_kampf as kampf_grafik
import neuropos
import math, copy, time

reload(neuropos)
reload(kampf_grafik)

window=kampf_grafik.window()

class projektil(object):
    """Ist Teil einer Attack und bewegt sich über den Bildschirm."""
    def __init__(self,attack,poslist):
        self.poslist=poslist
        self.pos = (0,0,0)
        self.size = 40
        self.color = (0,0,255)
        self.attack = attack
        self.counter = 0

    def read_poslist(self):
        posdata = self.poslist[self.counter]
        self.pos = posdata[0]
        if len(posdata) > 1:
            self.size = posdata[1]
            if len(posdata) > 2:
                self.color = posdata[2]

    def get_drawpos(self):
        x,y,z=self.pos

        if self.attack.followshildi:
            if self.attack.addshildidirection:
                angle=self.attack.shildi.direction
                x,y =(x*math.cos(angle)+y*math.sin(angle),
                      x*math.sin(angle)-y*math.cos(angle))

            x,y,z=(x+self.attack.shildi.pos[0],
                   y+self.attack.shildi.pos[1],
                   z+self.attack.shildi.pos[2])
        else:
            if self.attack.addshildidirection:
                angle=self.attack.direction
                x,y =(x*math.cos(angle)+y*math.sin(angle),
                      x*math.sin(angle)-y*math.cos(angle))

            x,y,z=(x+self.attack.startpos[0],
                   y+self.attack.startpos[1],
                   z+self.attack.startpos[2])

        if self.attack.addshildispeed:
            if type(self.attack.addshildispeed) in (list,tuple):
                x,y,z=(x+self.attack.startspeed[0]*self.counter*
                       self.attack.addshildispeed[0],
                       y+self.attack.startspeed[1]*self.counter*
                       self.attack.addshildispeed[1],
                       z+self.attack.startspeed[2]*self.counter*
                       self.attack.addshildispeed[2])
            else:
                x,y,z=(x+self.attack.startspeed[0]*self.counter,
                       y+self.attack.startspeed[1]*self.counter,
                       z+self.attack.startspeed[2]*self.counter)

        return (x,y,z)

    def __cmp__(self,other): #Kollisionsabfrage durch projektil == projektil
        (x1,y1),(x2,y2) = self.pos,other.pos
        d_qad=(x1-x2)**2+(y1-y2)**2
        return d_qad<=(self.size+other.size)**2

    def remove(self):
        self.attack.projektile.remove(self)

    def collision(self,other):
        pass

    def update(self):
        if self.counter >= len(self.poslist):
            self.remove()
            return
        self.read_poslist()
        drawpos=self.get_drawpos()
        if drawpos[2]>=0:
            window.drawsphere(drawpos,self.size,self.color)
        self.counter+=1

class Attack(object):
    """Attacke die ein Shildimon kann."""
    def __init__(self,shildi,(projektilliste,followshildi,
                    addshildispeed,addshildidirection,relaxtime)):
        self.shildi = shildi
        self.projektilliste = projektilliste
        self.followshildi = followshildi
        self.addshildispeed = addshildispeed
        self.addshildidirection = addshildidirection
        self.projektile = []
        self.startpos = copy.copy(self.shildi.pos)
        self.startspeed = copy.copy(self.shildi.speed)
        self.direction = copy.copy(self.shildi.direction)
        for poslist in self.projektilliste:
            self.projektile.append(projektil(self,poslist))

    def update(self):
        for projektil in self.projektile:
            projektil.update()
        if len(self.projektile)==0:
            self.shildi.runningattacks.remove(self)

class Shildimon(object):
    """Shildimon ... tbc"""
    def __init__(self, art):
        self.ART = "kaliper"                #Momentan noch kein Effekt
        self.KP = 100                       #dito
        self.KP_MAX = 100                   #dito
        self.LP = 100                       #dito
        self.LP_MAX = 100                   #dito
        self.ATTACKEN = [tackle,shot,shot2] #attacken siehe unten
        self.SIZE = 20                      #Kollisionsradius und Darstellungsgröße
        self.SLIDING = 0.5                  #Verzögerung beim Beschleunigen und Bremsen (0-1)
        self.MAX_SPEED = 20                 #Maximale Geschwindigkeit des Shildis in px/frame (>0)
        self.JUMP_POWER = 10                #Beschleunigung beim absprung (>0)
        self.JUMP_EXTEND = 2                #Verlangsamen des Falls durch gedrückt halten der Sprungtaste (wenn größer als GRAVITY->fliegen)
        self.AIR_HANDLING = 0.2             #Verzögerung beim Beschleunigen und Bremsen in der Luft (0-1)
        self.GRAVITY = 1                    #Fallbeschleunigung
        self.BUMPING = 0                    #Federn beim Aufprall (0-1)
        self.TURNING = 0.3                  #Verzögerung beim drehen
        self.direction = 0
        self.accel = self.MAX_SPEED*(1-self.SLIDING)
        self.air_accel = self.MAX_SPEED*(self.AIR_HANDLING)

        self.pos = [100,100,10]
        self.speed = [0,0,0]
        self.runningattacks = []
        self.relax_time = time.time()
        self.KEY_NR_TO_ACTION={
    kampf_grafik.K_UP    : lambda:self.addspeed(0, 1,0),
    kampf_grafik.K_DOWN  : lambda:self.addspeed(0,-1,0),
    kampf_grafik.K_RIGHT : lambda:self.addspeed( 1,0,0),
    kampf_grafik.K_LEFT  : lambda:self.addspeed(-1,0,0),
    kampf_grafik.K_SPACE : self.jump,
    kampf_grafik.K_1     : lambda:self.start_attack(0),
    kampf_grafik.K_2     : lambda:self.start_attack(1),
    kampf_grafik.K_3     : lambda:self.start_attack(2),
    kampf_grafik.K_4     : lambda:self.start_attack(3),
    kampf_grafik.K_5     : lambda:self.start_attack(4),
    kampf_grafik.K_6     : lambda:self.start_attack(5),
    kampf_grafik.K_7     : lambda:self.start_attack(6),
    kampf_grafik.K_8     : lambda:self.start_attack(7),
    kampf_grafik.K_9     : lambda:self.start_attack(8),
    kampf_grafik.K_0     : lambda:self.start_attack(9),}

    def addspeed(self,x,y,z):
        if self.pos[2]>0:
            x*=self.air_accel;y*=self.air_accel;z*=self.air_accel
        else:
            x*=self.accel;y*=self.accel;z*=self.accel
        self.speed=[self.speed[0]+x,self.speed[1]+y,self.speed[2]+z]

    def jump(self):
        if self.pos[2]>0:
            self.speed[2]+=self.JUMP_EXTEND
        elif abs(self.speed[2])<self.JUMP_POWER:
            self.speed[2]=self.JUMP_POWER

    def do_action(self,key_nr):
        if key_nr in self.KEY_NR_TO_ACTION.keys():
           self.KEY_NR_TO_ACTION[key_nr]()

    def start_attack(self,attacknumber):
        if attacknumber < len(self.ATTACKEN) and time.time(
            )-self.relax_time > self.ATTACKEN[attacknumber][-1]:
            chosen_attack=Attack(self,self.ATTACKEN[attacknumber])
            self.runningattacks.append(chosen_attack)
            self.relax_time+=self.ATTACKEN[attacknumber][-1]

    def update(self):
        self.pos[0]+=self.speed[0]
        self.pos[1]+=self.speed[1]
        self.pos[2]+=self.speed[2]

        for i in (0,1):
            if abs(self.speed[i])<min(self.MAX_SPEED*0.1,1):
                self.speed[i]=0

        if self.speed[0]!=0 or self.speed[1]!=0:
            direction=math.atan2(self.speed[1],self.speed[0])
            if (direction-self.direction-self.TURNING)%(2*math.pi)<math.pi:
                self.direction+=self.TURNING
            elif (self.direction-direction-self.TURNING)%(2*math.pi)<math.pi:
                self.direction-=self.TURNING
            else:
                self.direction=direction

        if self.pos[2]<=0:
            self.speed[0]*=self.SLIDING
            self.speed[1]*=self.SLIDING
        else:
            self.speed[0]*=1-self.AIR_HANDLING
            self.speed[1]*=1-self.AIR_HANDLING
        if self.pos[2]<=0:
            if self.speed[2]<-self.GRAVITY-1:
                self.speed[2]*=-self.BUMPING
                if self.speed[2]<self.GRAVITY:
                    self.pos[2]=0
                    self.speed[2]=0
            elif self.speed[2]<self.GRAVITY:
                self.pos[2]=0
                self.speed[2]=0
        else:
            self.speed[2]-=self.GRAVITY

        for attack in self.runningattacks:
            attack.update()
        #window.drawsphere(self.pos, self.SIZE, (0,255,0))
        window.drawshildimon(self.pos, self.SIZE,self.ART,self.direction*180/math.pi)


t_projektilliste=[[[(10,0,0),20,(0,0,255)]]]
t_followshildi=True
t_addshildispeed=False
t_addshildidirection=True
relaxtime=0.2
tackle=(t_projektilliste,t_followshildi,t_addshildispeed,
        t_addshildidirection,relaxtime)

s_projektil=[[(0,0,5),2,(255,0,0)]]
for i in range(100):
    s_projektil.append([(i*10,0,5)])
s_projektilliste=[s_projektil]
s2_projektil=[[(0,0,0),2,(255,0,0)]]
s2_speed=[10,0,10]
s2_pos=[0,0,0]
for i in range(100):
    s2_speed=s2_speed[0]*0.9,s2_speed[1]*0.9,s2_speed[2]-1
    s2_pos=[s2_pos[0]+s2_speed[0],s2_pos[1]+s2_speed[1],
            s2_pos[2]+s2_speed[2]]
    s2_projektil.append([s2_pos])
s2_projektilliste=[s2_projektil]
shot=(s_projektilliste,False,(1,1,0),True,0.1)
shot2=(s2_projektilliste,False,True,True,0.1)

def collision_detect(*shildis):
    pass

def kampf():
    ende = False
    testi = Shildimon("Testi")
    while not ende:
        window.new_frame()
        testi.update()
        collision_detect(testi)
        window.drawrelaxtime(time.time()-testi.relax_time)
        window.update()
        #neuropos.set(testi.pos,testi.speed)
        key_state = window.get_key_state()
        if key_state == kampf_grafik.K_QUIT:
            ende=True
        else:
            for key in key_state:
                testi.do_action(key)


if __name__=="__main__":
    window.setsource("/home/joram/Programmierung/Shildiwelt1.9/data/Objekte/Shildis/")
    kampf()
    import pygame
    pygame.quit()
