#!/usr/bin/env python

print "test"

import sys
sys.path.insert(0,"..")

import socket_connection
reload(socket_connection)

server = socket_connection.server()

while True:
    for msg,addr in server.receive():
        print msg
        server.send("answer"+msg,addr)
