# -*- coding: utf-8 -*-
import select, socket, time


class template():
    def __init__(self):
        pass
    
    def t_init(self):
        self.packagesize = 10000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(("", self.port))
        except socket.error, why:
            print "socket error: %s" % why
            return
        else:
            print self.port

    def send(self,msg,addr):
        msg = msg+"\n"
        self.socket.sendto(msg,addr)

class server(template):
    def __init__(self,port=40000,name="NONAME"):
        self.port = port
        self.name = name
        self.msgcache = {} #{addr:msg,...}
        self.t_init()

    def receive(self):
        received=[]
        while select.select([self.socket], [], [],0.001)[0]:
            data, addr = self.socket.recvfrom(self.packagesize)
            if data == "PING":
                self.socket.sendto("PONG"+self.name, addr)
            else:
                try:
                    self.msgcache[addr]+=data
                except KeyError:
                    self.msgcache[addr]=data
                if data[-1] in ("\n","\r"):
                    received.append((self.msgcache[addr],addr))
                    self.msgcache[addr] = ""
        return received

    def close(self):
        for addr in self.msgcache.keys():
            self.socket.sendto("shutdown",addr)
        self.socket.close()


class client(template):
    def __init__(self,serveraddr,port=40001):
        self.port = port
        self.serveraddr = serveraddr
        self.t_init()

    def ask(self,msg,timeout=1):
        self.send(msg,self.serveraddr)

        answer=""
        while True:
            if select.select([self.socket],[],[],timeout)[0]:
                data, addr = self.socket.recvfrom(self.packagesize)
                if addr == self.serveraddr:
                    answer+=data
                    if data[-1] in ("\n","\r"):
                        return answer
            else:
                break
        return answer

    def close(self):
        self.socket.sendto("bye",self.serveraddr)
        s.close()

def search_servers(waittime=3,port=40000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.sendto("PING", ("<broadcast>", port))
    except socket.error, why:
        s.close()
        return []

    servers = []
    if select.select([s], [], [], waittime)[0]:
        data, addr = s.recvfrom(100)
        if data.startswith("PONG") and not addr[0] in servers:
            #try:
            #    name = socket.gethostbyaddr(addr[0])[0] + " (" + addr[0] + ")"
            #except socket.error:
            #    name = addr[0]
            #clients.append((name,data[4:]))
            clients.append((addr,data[4:]))
    s.close()
    return servers


if __name__ == "__main__":
    eingabe=None
    
    while not eingabe=="quit":
        eingabe=raw_input(">>> ")
        if eingabe=="search":
            servers = search_servers()
            if servers != []:
                for i,(addr,name) in enumerate(clients):
                    print i, name, addr
            raw_input("wait")
            
        if eingabe=="start":
            print "spiel gestartet"
            for client,name in clients:
                client = client.split("(")[1].split(")")[0]
                mysocket.sendto("hallo mama",(client,port))
            while True:
                if select.select([mysocket], [], [], 0.2)[0]:
                    data, addr = mysocket.recvfrom(13)
                    print data
                else:
                    break
            print "spiel beendet"
        if eingabe=="shutdown_server":
            for client,name in clients:
                client = client.split("(")[1].split(")")[0]
                mysocket.sendto("quit",(client,port))
        if eingabe=="help":
            print """
show:   shows connections
search: searchs for computers and connects to them
start:  starts new game (for test only sends 1 message yet)
        then recieves answer of server
quit:   shutting down client
shutdown_server: send shutdownsignal to server
"""
    mysocket.close()
