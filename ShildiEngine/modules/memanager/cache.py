import random, time
import thread

class Cache(dict):
    """
    Cache that by default avoids Ping-Pong effect by random filtering of input.
    Might react too slow for some aaabbbccc... like sequences
    special methods for loading and saving data are __pull__ and __push__
    but saving data may still course bug
    """
    
    def __init__(self,loadfunc,maxn=None,maxt=None,dt=1,decide=lambda k,v:random.random()<0.1,*args,**kwargs):
        """
        (*args and **kwargs are forwarded to dict.__init__)
        """
        dict.__init__(self,*args,**kwargs)
        self.__pull__ = loadfunc
        self.decide = decide
        self.maxn = maxn # maximum number of elements
        self.maxt = maxt # maximum time to stay when unused for an element
        self.dt = dt
        if self.maxt:
            thread.start_new_thread(self.clearloop,())

    def __setitem__(self,key,value):
        self.__push__(key,value)
        dict.__setitem__(self,key,value)

    def __getitem__(self,key):
        value = dict.__getitem__(self,key)
        value[0] = time.time()
        return value[1]

    def __missing__(self,key):
        value = [0,self.__pull__(key)]
        if self.decide(key,value):
            if len(self)==self.maxn:
                oldest = min(dict.iteritems(self),key=lambda (k,v):v[0])
                self.pop(oldest[0])
            dict.__setitem__(self,key,value)
        return value

    def clearloop(self):
        try:
            while True:
                time.sleep(self.dt)
                t = time.time()-self.maxt
                for key,value in filter(lambda (k,v):v[0]<t,dict.iteritems(self)):
                    self.pop(key,None)
        except AttributeError:
            pass

if __name__ == "__main__":

    def loadvalue(key):
        return key+1
    
    d = Cache(loadvalue,maxn=20,maxt=5)

    while True:
        k = int(random.expovariate(0.2))
        d[k]
        k = int(random.randint(0,10))
        d[k]
        print d.keys()
        import time
        time.sleep(0.04)