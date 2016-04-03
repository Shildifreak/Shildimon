from time import time

class Laufzeitaufrufer():
    funcs = []
    rounds = 0
    starttime=time()
    funcindex=0
    
    def putin(self,func,speedinseconds):
        self.funcs.append([func,speedinseconds,1,self.funcindex])
        self.funcindex += 1

    def loop(self):
        for i in self.funcs:
            if (time()-self.starttime)/i[2]>i[1]:
                i[0]()
                self.funcs[i[3]][2]+=1


if __name__ == "__main__":
    ende = False
    def func1():
        pass
        print time()
    def func2():
        global ende
        print "ende"
        ende = True
    immerwieder=Laufzeitaufrufer()
    immerwieder.putin(func1,1)
    immerwieder.putin(func2,10)
    while ende == False:
        immerwieder.loop()
