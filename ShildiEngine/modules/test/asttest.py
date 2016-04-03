# -*- coding: utf-8 -*-
import ast
import codecs

out = codecs.open("myFile.py","w",encoding="utf-8")


data = {"size": [1,1],
        "name": "Landschaftsname",
        "music": "bgmusic.mp3",
        (0,0): {
            "action":"23",
            "background":"boden.png",
            "file":"gras.png",
                },
        "0": "test",
        "1": u"töööst!!!",
        }
#data["circle"]=data

def mypprint(data,out,current_indent=0):
    """
    pretty printing of nested literals to file
    optimized for shildimon game data
    fails on self containing lists/dicts!!!
    """
    if type(data) == dict:
        out.write("{\n")
        out.write(" "*current_indent)
        maxwidth = max(len(repr(x)) for x in data.iterkeys())
        for name, objekt in sorted(data.iteritems()):
            if type(objekt) == dict:
                out.write("\n")
                out.write(" "*current_indent)
            out.write(repr(name))
            out.write(" "*(maxwidth-len(repr(name))))
            out.write(" : ")
            mypprint(objekt,out,current_indent+2)
            out.write(", \n")
            out.write(" "*current_indent)
        out.write("}")
    elif type(data) in (str,unicode):
        out.write('"'+data+'"')
    else:
        out.write(repr(data))


import time
t1 = time.time()
mypprint(data,out)
t2 = time.time()
print t2-t1
out.close()

fin = codecs.open("myFile.py","r",encoding="utf-8")
data = ast.literal_eval(fin.read())
print data["1"]
fin.close()