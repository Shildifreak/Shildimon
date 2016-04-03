import sys
sys.path.insert(0,"..")

import socket_connection
reload(socket_connection)

servers = socket_connection.search_servers()

if servers != []:
    for i in range(len(servers)):
        print i,servers[i]
    n = int(raw_input("which one?"))
    server = servers[n][0]
    print server
    client = socket_connection.client(server)

    text = ""
    while text not in ("quit","q","exit"):
        text = raw_input("text: ")
        print client.ask(text)
