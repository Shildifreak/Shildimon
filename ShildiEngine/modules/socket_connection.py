# -*- coding: utf-8 -*-
import select, socket, time, sys


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
            pass
            #print "opened socket at port",self.port

    def send(self,msg,addr):
        if "\n" in msg:
            sys.stderr.write("message must not contain linebreaks")
            return
        msg = msg+"\n"
        self.socket.sendto(msg,addr)

class server(template):
    def __init__(self,port=40001,name="NONAME"):
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
                    received.append((self.msgcache[addr][:-1],addr))
                    self.msgcache[addr] = ""
        return received

    def close(self):
        for addr in self.msgcache.keys():
            self.socket.sendto("shutdown",addr)
        self.socket.close()


class client(template):
    def __init__(self,serveraddr,port=40000):
        self.port = port
        self.serveraddr = serveraddr
        self.t_init()

    def ask(self,msg,timeout=1):
        """
        returns False if server does not respond within timeout
        """
        self.send(msg,self.serveraddr)

        answer=""
        while True:
            if select.select([self.socket],[],[],timeout)[0]:
                data, addr = self.socket.recvfrom(self.packagesize)
                if addr == self.serveraddr:
                    answer+=data
                    if data[-1] in ("\n","\r"):
                        return answer[:-1]
            else:
                break
        return False

    def close(self):
        self.socket.sendto("bye",self.serveraddr)
        self.socket.close()

def search_servers(waittime=3,port=40001):
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
            servers.append((addr,data[4:]))
    s.close()
    return servers

if __name__ == "__main__":
    while True:
        eingabe = raw_input(">>> ")
        if eingabe == "quit":
            break

        if eingabe == "search":
            servers = search_servers()
            if servers != []:
                for i,(addr,name) in enumerate(servers):
                    print i, name, addr
            else:
                print "no servers found"

        if eingabe == "client":
            print "spiel gestartet"
            servers = search_servers()
            if servers != []:
                addr,name = servers[0]
                print "connecting to server %s" %name
                c = client(addr)
                while True:
                    eingabe = raw_input("send@server: ")
                    if eingabe == "close":
                        break
                    print c.ask(eingabe)
                c.close()
            else:
                print "no server found"
        
        if eingabe == "server":
            s = server()
            while True:
                for msg,addr in s.receive():
                    print "received:",repr(msg)
                    reply = "reply:"+msg
                    s.send(reply,addr)
                    if msg == "shutdown":
                        break
                else:
                    continue
                break
            s.close()

        if eingabe == "help":
            print """
show:   shows connections
search: searchs for computers and connects to them
start:  starts new game (for test only sends 1 message yet)
        then recieves answer of server
quit:   shutting down client
shutdown_server: send shutdownsignal to server
"""
