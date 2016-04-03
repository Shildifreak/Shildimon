# -*- coding: utf-8 -*-
import cache
import ast
import codecs
import os

# Soll folgendes machen:
# objects = Filehandler("")
# key = [[0,0],image]
# objects[key] -> boden.png
# objects[key] = gras.png
# objects.save()

# key soll so viele Argumente haben dürfen wie es lustig ist
# Ordnerstrukturen sollen als dictionarys aufgefasst werden
# Verschiedene Formate lesen zulassen

if False:    
    ############# Zeugs, wo ich Schnipsel von will (vielleicht)

    def saveNclear(self):
        print("saving data")
        #clear empty attributes
        for objectname,data in self.objects.items():
            if data != None:
                for var,val in data.items():
                    if val == "":
                        if self.configparser.has_section(objectname):
                            self.configparser.remove_option(objectname,var)
                        self.objects[objectname].pop(var)
            else:
                self.objects.pop(objectname)
                if self.configparser.has_section(objectname):
                    self.configparser.remove_section(objectname)
        for objectname,data in self.objects.items():
            # update staticobjparser for later request
            if "@" in objectname:
                if self.staticobjfile != objectname.split("@")[1]:
                    fn=os.path.join(self.objdir,objectname.split("@")[1]+".shl")
                    self.staticobjparser = ConfigParser.ConfigParser()
                    self.staticobjparser.read(fn)
                    self.staticobjfile = objectname.split("@")[1]
            # see if @-object is the same like in file
            if ("@" in objectname and \
                self.staticobjparser.has_section(objectname.split("@")[0]) and \
                data == dict(self.staticobjparser.items(objectname.split("@")[0]))):
                # if so, delete
                if self.configparser.has_section(objectname):
                    self.configparser.remove_section(objectname)
            # all other objects are refreshed
            else:
                if not self.configparser.has_section(objectname):
                    self.configparser.add_section(objectname)
                for var,val in data.items():
                    self.configparser.set(objectname,var,val)
        # and saved to file
        configdatei=open(self.filename, 'wb')
        self.configparser.write(configdatei)
        configdatei.close()
        print("clearing cache")
        self.objects.clear()
        #for d in self.splitcache.values(): #M# no splitcache by now
        #    d.clear()

    def get_object(self,name):
        obj = self.objects.get(name,None)
        if not obj:
            self.loadobject(name)
            obj = self.objects.get(name,None)
        return obj

    def get_attributelist(self,objekt):
        if not self.objects.has_key(objekt):
            self.loadobject(objekt)
        return self.objects[objekt].keys()


    #M# List attributes are depreciated, please don't use them :)
    def split(self,string):
        if "(" not in string:
            return string.split(",")
        raise NotImplementedError("The Split Method of the Interpreter doesn't suppert paranthesis by now. You shouldn't use it anyways.")
    
    def setlistattr(self,objekt,attribute,value,index):
        attributes = self.split(self.get_attribute(objekt,attribute))[:] #copy is important, so we can use inplace editing
        attributes[index] = value
        self.set_attribute(objekt,attribute,self.list2str(attributes))

    def add2listattr(self,objekt,attribute,value,index=None):
        if index == None:
            liststr = self.get_attribute(objekt,attribute)
            if liststr != "":
                liststr += ","
            liststr += value
            self.set_attribute(objekt,attribute,liststr)
        else:
            attributes = self.split(self.get_attribute(objekt,attribute))[:] #copy is important, so we can use inplace editing
            attributes.insert(index,value)
            self.set_attribute(objekt,attribute,self.list2str(attributes))

    def delfromlistattr(self,objekt,attribute,value):
        attributes = self.split(self.get_attribute(objekt,attribute,""))[:] #copy, so we can use remove command (inplace)
        while value in attributes:
            attributes.remove(value)
        self.set_attribute(objekt,attribute,self.list2str(attributes))
    # ----------------------------------------------------------

    def create_object(self,name):
        if not self.objects.has_key(name):
            self.objects[name] = {}
        else:
            print "Error: object name %s already in use" %name
            return False

    def delete_object(self,name):
        if self.objects.has_key(name):
            self.objects[name] = None


# ---------- FILETYPE SPECIFIC CLASSES ----------#

class MycfgFile:
    def read(self,file):
        lines = file.readlines()
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
            while trailingspace < current_indent:
                current_indent,current_dict = stack.pop(-1) # stop using subdict
            if line.startswith("["):
                if stack and (current_indent == stack[-1][0]):
                    current_indent,current_dict = stack.pop(-1) # stop using subdict
                new_dict = {}
                current_dict[line[1:-1]]=new_dict
                stack.append((current_indent,current_dict))
                current_indent,current_dict = None,new_dict # use new subdict
            else:
                seppos = line.replace("\\=","  ").find("=")
                key = line[:seppos].rstrip()
                value = line[seppos+1:].lstrip().rstrip()
                current_dict[key] = value
        return data

    def write(self,file,data,current_indent=0,alwaysindent=True):
        """
        pretty printing of nested literals to file
        optimized for shildimon game data
        fails on self containing lists/dicts!!!
        set alwaysindent to False for partial backward compatibility
        """
        if isinstance(data,dict):
            # NonSubdicts
            maxwidth = max(len(repr(x)) for x in data.iterkeys())
            otheritems   = ((k,v) for k,v in data.iteritems() if type(v) != dict)
            for name, objekt in sorted(otheritems):
                file.write(" "*current_indent)
                file.write(str(name).replace("\\","\\\\").replace("=","\\=").replace("\n","\\n")) # escaping
                file.write(" "*(maxwidth-len(repr(name))))
                file.write(" = ")
                self.write(file,objekt,current_indent+2,alwaysindent)
                file.write("\n")
            # Subdicts
            subdictitems = ((k,v) for k,v in data.iteritems() if type(v) == dict)
            for name, objekt in sorted(subdictitems):
                file.write(" "*current_indent)
                file.write("\n"+" "*current_indent)
                file.write("["+str(name)+"]")
                file.write("\n")
                containsdict = sum((type(obj) == dict) for obj in objekt.itervalues())
                if containsdict or alwaysindent:
                    self.write(file,objekt,current_indent+2,alwaysindent)
                else:
                    self.write(file,objekt,current_indent,alwaysindent)

        elif type(data) in (str,unicode):
            file.write(data)
        elif type(data) in (int,tuple,list):
            file.write(repr(data))
        else:
            raise NotImplementedError

# ---------- Basic File Handler -----------------#

class NestedDict(dict):
    def __getitem__(self,keys):
        if type(keys) not in (list,tuple):
            return dict.__getitem__(self,keys)
        value = self
        for i,key in enumerate(keys):
            try:
                value = dict.__getitem__(value,key)
            except KeyError as ke:
                ke.args = (i,)+ke.args
                raise ke
        return value
    def __setitem__(self,keys,value):
        if type(keys) not in (list,tuple):
            return dict.__setitem__(self,keys,value)
        self[keys[:-1]][keys[-1]]=value

class BasicFileHandler:
    FILETYPES = {"cfg":MycfgFile(),
                 "shl":MycfgFile(),
                 #"py":PyAstFile(),
                 #"json":JsonFile(),
                 }

    def __init__(self):
        # cache.Cache related stuff
        decide = lambda k,v:True #random.random()<0.1
        self.filecache = cache.Cache(self._readfile,maxn=None,maxt=10,decide=decide) #use only for static files

    def readfile(self,path):
        return self.filecache[path]

    def _readfile(self,path):
        filetype = path.rsplit(".",1)[1]
        with codecs.open(path,"r",encoding="utf-8") as f:
            return NestedDict(self.FILETYPES[filetype].read(f))

    def writefile(self,path,data):
        filetype = path.rsplit(".",1)[1]
        with codecs.open(path,"w",encoding="utf-8") as f:
            self.FILETYPES[filetype].write(f,data)

class FileHandler(BasicFileHandler):
    """use subclasses with replaced readfile and writefile methods!"""
    def __init__(self,savefilename,gamedir):
        BasicFileHandler.__init__(self)
        # loading data
        self.savefilename = savefilename
        self.gamedir = gamedir
        self.varset_func = lambda keys,old,new:None#None
        if os.path.exists(savefilename):
            self.objects = self.readfile(savefilename)
        else:
            self.objects = NestedDict()

    def __setitem__(self,keys,value):
        if isinstance(keys,str):
            keys = keys.split(".")
        if type(keys) not in (list,tuple):
            raise ValueError("keys has to be of type list or tuple")
        if self.varset_func != None:
            valueold = self[keys]
        self.objects[keys] = value
        if self.varset_func != None:
            self.varset_func(keys,valueold,value)

    def __getitem__(self,keys,default="default"):
        """Mit default"""
        if isinstance(keys,str):
            keys = keys.split(".")
        if type(keys) not in (list,tuple):
            raise ValueError("keys has to be of type list or tuple")
        try:
            return self._getitem(keys)
        except KeyError:
            return default

    def _getitem(self,keys,blocked=(),inheritblocked=(),i_ib=None):
        """
        ohne default, aber mit inherit und nachgeladen wenn nötig
        gibt bei zugriffsfehler die Stelle mit zurück
        """
        #print "trying to read", keys
        if keys in blocked:
            if "--debug" in sys.argv:
                sys.stderr.write("[DEBUG] Reading %s got blocked. Circular reference?\n" %keys)
            raise KeyError("Reading %s got blocked. Circular reference?" %keys)
        try:
            return self.objects[keys]
        except KeyError as objectserror:
            try:
                return self.get_original(keys)
            except KeyError as originalerror:
                i = max(objectserror.args[0],originalerror.args[0])
                if keys[i] == "inherit": # searching for inherit attribute that wasn't found is pointless
                    raise KeyError()
                if i < i_ib:
                    blocked += inheritblocked
                parents = self._getitem(keys[:i]+["inherit"],blocked)
                if isinstance(parents,basestring):
                    parents = parents.split(",")
                for parent in parents:
                    if isinstance(parent,basestring):
                        parent = parent.split(".")
                    try:
                        return self._getitem(parent+keys[i:],blocked+(keys,),(keys[:i]+["inherit"],),len(parent))
                    except:
                        raise
                raise

    def get_original(self,keys):
        path = self.gamedir
        ikeys = iter(("main",)+tuple(keys))
        for key in ikeys:
            if not os.path.isdir(os.path.join(path,key)):
                break
            path = os.path.join(path,key)
        left_keys = list(ikeys)
        # search in dir
        try:
            for f in os.listdir(path):
                if key == f.rsplit(".")[0]:
                    return self.readfile(os.path.join(path,f))[left_keys]
        except KeyError as e:
            e.args = (e.args[0]+len(keys)-len(left_keys),)+e.args[1:]
            raise e
        # search in file
        try:
            for f in os.listdir(os.path.dirname(path)):
                if os.path.isdir(os.path.join(os.path.dirname(path),f)):
                    continue
                if os.path.basename(path) == f.rsplit(".")[0]:
                    data = self.readfile(os.path.join(os.path.dirname(path),f))
                    return data[[key]+left_keys]
        except KeyError as e:
            e.args = (e.args[0]+len(keys)-len(left_keys)-1,)+e.args[1:]
            raise e

    def save(self):
        raise NotImplementedError

if __name__ == "__main__":
    import sys
    sys.argv.append("--debug")
    data = {"size": [1,1],
            "name": "Landschaftsname",
            "music": "bgmusic.mp3",
            "[0,0]": {
                "action":"23",
                "background":"boden.png",
                "file":"gras.png",
                    },
            "0": "test",
            "1": u"töööst!!!",
            }
    # Write
    bfh = BasicFileHandler()
    bfh.writefile("test.shl",data)
    # Read
    data = bfh.readfile("test.shl")
    MycfgFile().write(sys.stdout,data)
    
    d = NestedDict(data)
    print d["[0,0]","action"]
    d["[0,0]","action"] = 24
    print d["[0,0]","action"]
    
    #
    fh = FileHandler("shildimon.shl","ShildimonCopy")
    print fh[[]]
    print fh[[""]]
    print fh[""]
    print fh[["joram"]]
    print fh["joram"]
    print fh[["joram","type"]]
    print fh["joram.type"]
    print fh["joram.age"]
    print fh["test1.nonexisting"]
    print fh["test3.nonexisting"]
    fh["test1"] = {}
    fh["test1.nonexisting"] = "not nonexisting anymore"
    print fh["test1.nonexisting"]