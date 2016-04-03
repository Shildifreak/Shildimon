# -*- coding: utf-8 -*-
import ast
import codecs

out = codecs.open("myFile.cfg","w",encoding="utf-8")


data = {"size": [1,1],
        "name": '"Landschaftsname"',
        "music": '"bgmusic.mp3"',
        "(0,0)": {
            "action":23,
            "back\\ground":'"boden.png"',
            "file":'"gras.png"',
            "more test": {
                1:2,
                3:4},
                },
        "0": "int:[time:[]]",
        "1": u'"töööst!!!"',
        }
#data["circle"]=data

def mypprint(data,out,current_indent=0,alwaysindent=True):
    """
    pretty printing of nested literals to file
    optimized for shildimon game data
    fails on self containing lists/dicts!!!
    set alwaysindent to False for partial backward compatibility
    """
    if type(data) == dict:
        # NonSubdicts
        maxwidth = max(len(repr(x)) for x in data.iterkeys())
        otheritems   = ((k,v) for k,v in data.iteritems() if type(v) != dict)
        for name, objekt in sorted(otheritems):
            out.write(" "*current_indent)
            out.write(str(name).replace("\\","\\\\").replace("=","\\=").replace("\n","\\n")) # escaping
            out.write(" "*(maxwidth-len(repr(name))))
            out.write(" = ")
            mypprint(objekt,out,current_indent+2,alwaysindent)
            out.write("\n")
        # Subdicts
        subdictitems = ((k,v) for k,v in data.iteritems() if type(v) == dict)
        for name, objekt in sorted(subdictitems):
            out.write(" "*current_indent)
            out.write("\n"+" "*current_indent)
            out.write("["+str(name)+"]")
            out.write("\n")
            containsdict = sum((type(obj) == dict) for obj in objekt.itervalues())
            if containsdict or alwaysindent:
                mypprint(objekt,out,current_indent+2,alwaysindent)
            else:
                mypprint(objekt,out,current_indent,alwaysindent)

    elif type(data) in (str,unicode):
        out.write(data)
    elif type(data) in (int,tuple,list):
        out.write(repr(data))
    else:
        raise NotImplementedError

def myread(lines):
    if lines[0].startswith("="):
        return lines[1:]
    data = {}
    stack = []
    current_indent = 0
    current_dict = data
    for rawline in lines:
        rawline = rawline[:-1]
        line = rawline.lstrip()
        # skip empty lines
        if len(line) == 0:
            continue
        # react to number of trailing space
        trailingspace = len(rawline) - len(line)
        if current_indent == None:
            current_indent = trailingspace # define indent of new subdict
        print "blah",trailingspace,current_indent
        while trailingspace < current_indent:
            current_indent,current_dict = stack.pop(-1) # stop using subdict
        if line.startswith("["):
            new_dict = {}
            current_dict[line[1:-1]]=new_dict
            stack.append((current_indent,current_dict))
            current_indent,current_dict = None,new_dict # use new subdict
        else:
            seppos = line.replace("\\=","  ").find("=")
            key = line[:seppos].rstrip()
            value = line[seppos+1:].lstrip().rstrip()
            print key+"|"+value
            current_dict[key] = value
    return data

mypprint(data,out)
out.close()

fin = codecs.open("myFile.cfg","r",encoding="utf-8")
rawdata = fin.readlines() #ast.literal_eval(fin.read())
data = myread(rawdata)
import sys
mypprint(data,sys.stdout)
fin.close()