# -*- coding: utf-8 -*-
import cache
import ast
import codecs
import os, sys
import copy

# Soll folgendes machen:
# objects = Filehandler("")
# key = ["main","[0,0]","image"]
# objects[key] -> boden.png
# objects[key] = gras.png
# objects.save()

# Verschiedene Formate lesen zulassen

if False:
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

class NestedDict:
    """
    Wrapper for nested dictionarys. Used for storing global kroet data.
    """
    encode_inherit = lambda self, string: [part.split(".") for part in string.split(",")]
    varset_func = lambda self,keys,old,new:None
    
    def __init__(self,data=None):
        if data:
            self.data = data
        else:
            self.data = {}

    def get(self,keys,default=""):
        """get supporting default value"""
        if isinstance(keys,basestring):
            keys = keys.split(".")
        if type(keys) not in (list,tuple):
            raise ValueError("keys has to be of type list or tuple")
        try:
            return self.__getitem__(keys)
        except KeyError:
            return default
    
    def __getitem__(self,keys,blocked=(),inheritblocked=(),i_ib=None):
        """standart get, that doesnt care about default values, but supports inherit"""
        if isinstance(keys,tuple):
            keys = list(keys)
        if keys in blocked:
            if "--debug" in sys.argv:
                sys.stderr.write("[DEBUG] Reading %s got blocked. Circular reference?\n" %keys)
            raise KeyError("Reading %s got blocked. Circular reference?" %keys)
        try:
            return self._rawget(keys)
        except KeyError as error:
            if not len(error.args):
                raise
            i = error.args[0]
            if keys[i] == "inherit": # searching for inherit attribute that wasn't found is pointless
                raise KeyError()
            if i < i_ib:
                blocked += inheritblocked
            parents = self.__getitem__(keys[:i]+["inherit"],blocked)
            parents = self.encode_inherit(parents)
            for parent in parents:
                try:
                    return self.__getitem__(parent+keys[i:],blocked+(keys,),(keys[:i]+["inherit"],),len(parent))
                except KeyError:
                    pass
            raise KeyError()

    def _rawget(self,keys):
        #print "trying to read %s" %keys
        if type(keys) not in (list,tuple):
            #print "keys:",keys
            raise ValueError()
        value = self.data
        for i,key in enumerate(keys):
            try:
                value = dict.__getitem__(value,key)
            except KeyError as ke:
                ke.args = (i,)+ke.args
                raise ke
            except TypeError as ke:
                raise KeyError()
        return value
    
    def __setitem__(self,keys,value):
        """standart set"""
        if self.varset_func != None:
            valueold = self.get(keys)
        self._rawset(keys,value)
        if self.varset_func != None:
            self.varset_func(keys,valueold,value)

    def _rawset(self,keys,value):
        if type(keys) not in (list,tuple):
            raise ValueError()
        container = self.data
        for key in keys[:-1]:
            try:
                new_container = container[key]
            except KeyError:
                new_container = None
            if not isinstance(new_container,dict):
                # create new subdict possibly overwriting nondict attribute!
                new_container = {}
                container[key] = new_container
            container = new_container
        container[keys[-1]] = value

    def walk(self,top = None,topkey=[]):
        if top == None:
            top = self.data
        items = []
        for key,value in top.iteritems():
            key = topkey+[key]
            if isinstance(value,dict):
                items.extend(self.walk(value,key))
            else:
                items.append((key,value))
        return items

class FileHandler2(NestedDict):
    FILETYPES = {"cfg":MycfgFile(),
                 "shl":MycfgFile(),
                 #"py":PyAstFile(),
                 #"json":JsonFile(),
                 }

    def __init__(self,savefilename,gamedir):
        NestedDict.__init__(self)
        # cache.Cache related stuff
        decide = lambda k,v:True #random.random()<0.1
        self.filecache = cache.Cache(self._readfile,maxn=None,maxt=10,decide=decide) #use only for static files
        # loading data
        self.savefilename = savefilename
        self.gamedir = gamedir
        if os.path.exists(savefilename):
            self.data = copy.deepcopy(self.readfile(savefilename)) #M# deepcopy necessary?

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

    def _rawget(self,keys):
        """
        replace _rawget of NestedDict
        """
        try:
            return NestedDict._rawget(self,keys)
        except KeyError as objectserror:
            try:
                value = self.get_original(keys)
            except KeyError as originalerror:
                if len(objectserror.args) and len(originalerror.args):
                    i = max(objectserror.args[0],originalerror.args[0])
                    raise KeyError(i)
                raise
            else:
                self._rawset(keys,copy.deepcopy(value))
                return value

    def get_original(self,keys):
        path = self.gamedir
        ikeys = iter(("main",)+tuple(keys))
        for key in ikeys:
            if not os.path.isdir(os.path.join(path,key)):
                break
            path = os.path.join(path,key)
        left_keys = list(ikeys)
        x = 0
        try:
            # search in dir
            for f in os.listdir(path):
                if key == f.rsplit(".")[0]:
                    return self.readfile(os.path.join(path,f))[left_keys]
            # search in file
            x = 1 # for error handling
            for f in os.listdir(os.path.dirname(path)):
                if os.path.isdir(os.path.join(os.path.dirname(path),f)):
                    continue
                if os.path.basename(path) == f.rsplit(".")[0]:
                    data = self.readfile(os.path.join(os.path.dirname(path),f))
                    return data[[key]+left_keys]
        except KeyError as e:
            if not len(e.args):
                raise
            e.args = (e.args[0]+len(keys)-len(left_keys)-x,)+e.args[1:]
            raise e

    def clear(self):
        raise NotImplementedError
        # test for every option whether it is different than the original one

    def save(self):
        for i in self.walk():
            dosave = False
            try:
                print i[0]
                if i[0] == ["joram","type"]:
                    print "HEY"
                    print self.get_original(i[0])
                    print i[1]
                if self.get_original(i[0]) != i[1]:
                    dosave = True
            except KeyError:
                dosave = True
            if dosave:
                print i
        raise NotImplementedError


class FileHandler:
    FILETYPES = {"cfg":MycfgFile(),
                 "shl":MycfgFile(),
                 #"py":PyAstFile(),
                 #"json":JsonFile(),
                 #"yaml":YamlFile(), #M#
                 }

    def __init__(self,gamedir=None,savefile=None):
        """
        lädt savefile nach data
        """
        self.gamedir = gamedir
        self.savefile = savefile
        # cache.Cache related stuff
        decide = lambda k,v:True #random.random()<0.1
        self.originals = cache.Cache(self.readfile,maxn=None,maxt=10,decide=decide) #use only for static files
        # the actual data
        self.data = {}      # {filename:datastructure,...}
        if savefile and os.path.exists(savefile):
            self.data = self._readfile(savefile)

    def readfile(self,filename):
        if self.gamedir:
            filename = filename.replace("\\","/")
            basename = os.path.splitext(os.path.basename(filename))[0]
            filedir = os.path.join(self.gamedir,os.path.dirname(filename))
            print "listing files of %r" %filedir
            for f in os.listdir(filedir):
                if basename == os.path.splitext(f)[0]:
                    print "opening %r" %f
                    return self._readfile(os.path.join(filedir,f))
        if "--debug" in sys.argv:
            print("file %r at %r not found" %(filename,self.gamedir))
        return {}

    def _readfile(self,path):
        filetype = path.rsplit(".",1)[1]
        with codecs.open(path,"r",encoding="utf-8") as f:
            return self.FILETYPES[filetype].read(f)

    def get(self,keys,default=None):
        return deepget((self.data,self.originals),keys,default)

    def set(self,keys,value):
        deepset(self.data,keys,value)

    def clear(self):
        """
        löscht redundante Informationen aus data
        """

    def save(self):
        """
        speichert data nach savefile
        """

MISSING = object()
def deepget(data,keys,default=MISSING):
    """
    data: sequence of dicts
    keys: sequence of keys
    -> value, todo
    bedeutet wenn todo None ist, ist value der erwartete Wert
             wenn todo eine Liste ist, ist value der inheritwert
             wenn todo False ist, wurde der default Wert genommen
    """
    for top in data:
        for i,key in enumerate(keys):
            if not isinstance(top,dict):
                raise ValueError("can't get attribute from nondict objekt %s" %top)
            try:
                top = top[key]
            except KeyError:
                if "inherit" in top:
                    return top["inherit"],keys[i:]
                else:
                    break
        else:
            return top,None
    if default == MISSING:
        raise KeyError(keys)
    return default,False

def deepset(container,keys,value):
    """
    setzt in container den entsprechenden Wert
    setzen von None löscht den Wert? #M#
    """
    if not isinstance(keys,(list,tuple)):
        raise ValueError()
    for key in keys[:-1]:
        try:
            new_container = container[key]
        except KeyError:
            new_container = None
        if not isinstance(new_container,dict):
            # create new subdict possibly overwriting nondict attribute!
            new_container = {}
            container[key] = new_container
        container = new_container
    container[keys[-1]] = value

def encode_inherit(string):
    if "@" in string:
        x = string.split("@")
        x[0] = x[0].split(".")
        return x
    return string.split(".")

def getitem(keys, fh2, default="default"):
    while True:
        if not isinstance(keys,list): # allow local vars to be without dot
            keys = [keys]
        if not isinstance(keys[0],list):
            pass
            # read tmp here
        else:
            plainkeys = [keys[1]]+keys[0]
            try:
                value, todo = fh2.get(plainkeys)
            except KeyError:
                return default
            if not todo:
                return value
            keys = encode_inherit(value)
            keys[0].extend(todo)
        raw_input(keys)

if __name__ == "__main__":
    fh = FileHandler("ShildimonCopy","shildimon.shl")
    print getitem([["joram","loopaction"],"main"],fh)
    print fh.get(["main","joram","loopaction"])

if False:#__name__ == "__main__":
    import sys
    sys.argv.append("--debug")
    data = {"size": [1,1],
            "name": "Landschaftsname",
            "music": "bgmusic.mp3",
            "[0,0]": {
                "action":"23",
                "inherit":"joram.test",
                "background":"boden.png",
                "file":"gras.png",
                    },
            "0": "test",
            "1": u"töööst!!!",
            }
    # Write
    #bfh = BasicFileHandler()
    #bfh.writefile("test.shl",data)
    # Read
    #data = bfh.readfile("test.shl")
    #MycfgFile().write(sys.stdout,data)
    
    d = NestedDict(data)
    print d["[0,0]","action"]
    d["[0,0]","action"] = 24
    print d["[0,0]","action"]
    
    #
    fh = FileHandler("shildimon.shl","ShildimonCopy")
    print fh[[]]
    #print fh.get("")
    print fh[["joram"]]
    print fh.get("joram")
    print fh[["joram","type"]]
    print fh.get("joram.type")
    print fh.get("joram.age")
    print fh.get("test1.nonexisting")
    print fh.get("test3.nonexisting")
    fh[["test1","nonexisting"]] = "not nonexisting anymore"
    print fh.get("test1.nonexisting")
    print "ORIGINAL:",fh.get_original(["joram","type"])
    fh[["joram","type"]] = "some new type"
    print "ORIGINAL2:",fh.get_original(["joram","type"])
    #fh[["joram","type","test"]] = "overwriting attribute with subdict"
    print fh.get("joram.type.test")
    
    fh[["TEST"]] = "test done"
        
    print "SAVING!"
    fh.save()

