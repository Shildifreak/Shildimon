import sys,os
import time
import ConfigParser
import StandartCommands
import memanager
if "--reload" in sys.argv:
    reload(StandartCommands)
    reload(memanager)
if "--debug" in sys.argv:
    DEBUG = True
else:
    DEBUG = False

TIMEOUT = RuntimeError("Timeout")

def encode_inherit(string): #M# dont use this but rather execute the line
    if "@" in string:
        x = string.split("@")
        x[0] = x[0].split(".")
        return x
    return string.split(".")

class Interpreter():
    def __init__(self,varset_func = None,filehandler = None): #M# ehemals objdir=None
        self.parser = Parser()
        if not filehandler:
            filehandler = memanager.FileHandler()
        self.filehandler = filehandler
        #self.objects = memanager.NestedDict()
        #self.objdir = objdir
        self.interrupted_funcs = []
        #self.varset_func = varset_func
        print "varset_func is currently ignored!"
        self.AdditionalCommandsets = []

    def open(self,savefilename,gamedir):
        self.save()
        self.filehandler = memanager.FileHandler(gamedir, savefilename)
        #self.objects = memanager.FileHandler(savefilename,gamedir)

    def save(self):
        if self.filehandler:
            self.filehandler.save()

    def get_var(self, plainkeys, default="default", envvar={}):
        if envvar: #M# delete this one day?
            raise Exception("Unexpexted error!")
        while True:
            value, todo = self.filehandler.get(plainkeys,default)
            if not todo:
                return value
            keys = encode_inherit(value) #M# to be replaced by execute
            if not (isinstance(keys,(list,tuple)) and isinstance(keys[0],(list,tuple))):
                raise ValueError("inherit must be global variable not %r" %value)
            plainkeys = [keys[1]]+keys[0]+todo

    # only for compatibility with server... may be removed if someone changes the server script to use get_var
    def get_attribute(self,objekt,attribute,default="",usetypeaction=True):
        if "@" in objekt:
            objekt,filename = objekt.split("@")
        else:
            filename = "main"
        return self.get_var([filename,objekt,attribute],default)

    def set_attribute(self,objekt,attribute,value):
        if "@" in objekt:
            objekt,filename = objekt.split("@")
        else:
            filename = "main"
        print "writing",[filename,objekt,attribute],value
        self.filehandler.set([filename,objekt,attribute],value)
        print "written"

    if False:

        def loadobject(self,objectname):
            raise NotImplementedError
            if self.objects.has_key(objectname):
                return None
            if self.configparser.has_section(objectname):
                self.objects[objectname] = dict(self.configparser.items(objectname))
                return True
            if "@" in objectname:
                if self.staticobjfile != objectname.split("@")[1]:
                    fn=os.path.join(self.objdir,objectname.split("@")[1]+".shl")
                    self.staticobjparser = ConfigParser.ConfigParser()
                    self.staticobjparser.read(fn)
                    self.staticobjfile = objectname.split("@")[1]
                if self.staticobjparser.has_section(objectname.split("@")[0]):
                    self.objects[objectname] = dict(self.staticobjparser.items(objectname.split("@")[0]))
                    return True
            self.objects[objectname] = None
            return False

        def saveNclear(self):
            raise NotImplementedError
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
            raise NotImplementedError
            obj = self.objects.get(name,None)
            if not obj:
                self.loadobject(name)
                obj = self.objects.get(name,None)
            return obj

        def get_attributelist(self,objekt):
            raise NotImplementedError
            if not self.objects.has_key(objekt):
                self.loadobject(objekt)
            return self.objects[objekt].keys()

        def get_attribute(self,objekt,attribute,default="",usetypeaction=True):
            raise NotImplementedError
            if not self.objects.has_key(objekt):
                self.loadobject(objekt)
            if self.objects[objekt] == None:
                return default
            ret = self.objects[objekt].get(attribute,"")
            if ret in [""]:
                if self.objects[objekt].has_key("inherit"):
                    return self.get_attribute(self.objects[objekt]["inherit"],attribute)
                return default
            return ret

        def set_attribute(self,objekt,attribute,value):
            raise NotImplementedError
            if not self.objects.has_key(objekt):
                self.loadobject(objekt)
            if self.objects[objekt] == None:
                self.objects[objekt] = {} #M# only here for testing - replace with error message later
            if self.varset_func != None:
                valueold = self.get_attribute(objekt,attribute)
                self.varset_func(objekt,attribute,valueold,value)
            self.objects[objekt][attribute] = value

    #M# List attributes are depreciated, please don't use them :) --> have to be removed from dialog functions
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
        self.filehandler.set(["main",name],{})

    def delete_object(self,name):
        self.filehandler.set(["main",name],None)

    def list2str(self,l):
        r = "".join([str(i)+"," for i in l])
        if r.endswith(","):
            r = r[:-1]
        return r

    def continue_execute(self,printstepinfo=False,stepbystep=False):
        new_states = []
        for state in self.interrupted_funcs:
            task = Task(**state)
            self._execute(task,printstepinfo,stepbystep)
            if not task.finished:
                new_states.append(task.to_literal())
        self.interrupted_funcs = new_states

    def execute(self,command,envvar=None,tmax=None,p=False,printstepinfo=False,stepbystep=False):
        try:
            parsed = self.parser.cached_parse(command)
            task = Task(parsed=parsed, envvar=envvar, t_max=tmax)
            self._execute(task,printstepinfo,stepbystep)
        except:
            print command
            raise
        if task.finished:
            return task.result
        else:
            self.interrupted_funcs.append(task.to_literal())
            return "no result yet" #no result yet

    def _execute(self, task, printstepinfo=False, stepbystep=False):
        # write, operator, operation, pack, case, jump, if0jump
        t = time.time()
        step = 0
        while True:
            cL = task.layers[-1] # currentLayer
            while (cL.i < cL.i_max):
                if task.t_max and (time.time()-t > task.t_max):
                    raise TIMEOUT
                action, parameter = cL.parsedexpression[cL.i]
                if action == "write":
                    cL.stack.append(parameter)
                    cL.i += 1
                elif action == "pack":
                    newlist = []
                    for j in range(parameter):
                        newlist.insert(0,cL.stack.pop(-1))
                    cL.stack.append(newlist)
                    cL.i += 1
                elif action in ("operator","unary operator","custom operation"):
                    if action == "operator":
                        operator = parameter
                        args = [cL.stack.pop(-2),cL.stack.pop(-1)]
                    elif action == "unary operator":
                        operator = parameter
                        args = [cL.stack.pop(-1)]
                    else:# action == "custom operation":
                        operator = cL.stack.pop(-1)
                        args = [cL.stack.pop(-2),cL.stack.pop(-1)]

                    while operator == ":":
                        operator = args[0]
                        if type(args[1]) in (list,tuple):
                            args = args[1]
                        else:
                            args = [args[1]]

                    if len(args) == 2:
                        leftarg = args[0]
                        rightarg = args[1]
                    
                    if operator == "#":
                        todo = []
                        keys = args[0]
                        default = ""
                        if len(args) > 1:
                            default = args[1]
                        while True:
                            if not isinstance(keys,(list,tuple)): #allow local vars to be without dot
                                keys = [keys]
                            if not isinstance(keys[0],(list,tuple)): #local var
                                result, todo = memanager.deepget((cL.tmpvar,),keys+todo,default)
                                if todo:
                                    keys = encode_inherit(result) #M# to be replaced by execute
                                    continue
                            else:
                                plainkeys = [keys[1]]+keys[0]+todo
                                result = self.get_var(plainkeys,default=default,envvar=cL.envvar)
                            break

                    elif operator == ":=":
                        if not isinstance(leftarg,(list,tuple)): # allow local vars to be without dot
                            leftarg = [leftarg]
                        if isinstance(leftarg[0],(list,tuple)):
                            self.filehandler.set([leftarg[1]]+leftarg[0],rightarg)
                        else:
                            memanager.deepset(cL.tmpvar,leftarg,rightarg)
                        result = rightarg
                    elif operator == "!":
                        if (type(leftarg) in (str,unicode)) and (type(rightarg) in (list,tuple)):
                            cL.i += 1
                            task.add_layer(self.parser.cached_parse(leftarg),dict(enumerate(rightarg)))
                            break
                        else:
                            raise TypeError("wrong type of argument(s) for operation %s" %operator)
                    elif type(operator) == int:
                        result = args[operator]
                    else:
                        try:
                            result = calculate(operator,args) # all the other operations that don't mess with memory
                        except NotImplementedError:
                            result = self.call_function(operator,args,cL)
                    cL.stack.append(result)
                    cL.i += 1
                elif action == "wait":
                    cL.i += 1
                    if task.t_max:
                        task.t_max -= time.time()-t
                    return
                elif action == "case":
                    index = cL.stack.pop(-1)
                    if type(index) != int:
                        raise TypeError("index in case structure must be of type integer")
                    if 0 < index < len(parameter):
                        cL.i += parameter[index-1]
                    else:
                        cL.i += parameter[-1]
                elif action == "jump":
                    cL.i += parameter
                elif action in ("if0jump","if1jump"):
                    condition = cL.stack.pop(-1)
                    if bool(condition) == (action=="if1jump"):
                        cL.i += parameter
                    else:
                        cL.i += 1
                else:
                    raise BaseException("Unknown action %s in parsed expression" %action)

                if printstepinfo:
                    print "step :",step,action
                    print "time :",time.time()-t
                    print "pos  :",cL.i
                    print "stack:",[l.stack for l in task.layers]
                    if stepbystep:
                        raw_input("---continue---")
                    else:
                        print "--------------"
                step += 1

            else: #from inner while loop, do not do the following, when recently created new substack
                task.layers.pop(-1)
                if len(cL.stack) != 1:
                    raise BaseException("Unexpected Error. Stack element number doesn't match.")
                if task.layers:
                    task.layers[-1].stack.append(cL.stack[0])
                else:
                    task.finished = True
                    task.result = cL.stack[0]
                    if printstepinfo:
                        print "time :",time.time()-t
                    return

    def call_function(self,func,args,currentLayer):
        envvar = currentLayer.envvar

        function = StandartCommands.commands.get(func,None)
        if function == None:
            for commandset in self.AdditionalCommandsets:
                function = commandset.get(func,None)
                if function != None:
                    break
        if function == None:
            print "function", func, "not found"
            function = StandartCommands.dummi
        return function((self,envvar),*args)

def calculate(operator,args):
    n = len(args)
    if n == 0:
        leftarg = rightarg = None
    elif n == 2:
        leftarg,rightarg = args
    elif n == 1:
        leftarg,rightarg = None,args[0]
    else:
        leftarg = calculate(operator,args[:-1])
        rightarg = args[-1]

    if operator in ("+","-","*","/","//","%","**","<","<=","==",">=",">","!=","<>"):
        if type(rightarg) in (list,tuple):
            if type(leftarg) in (list,tuple): # Array, Array
                return [calculate(operator,[leftarg[i],rightarg[i]]) for i in xrange(min(len(leftarg),len(rightarg)))]
            return [calculate(operator,[leftarg,i]) for i in rightarg]
        if type(leftarg) in (list,tuple): # Array, ? -> elementwise too
            return [calculate(operator,[i,rightarg]) for i in leftarg]
        if operator == "+":
            return leftarg + rightarg
        elif operator == "-":
            if leftarg == None:
                return -rightarg
            else:
                return leftarg - rightarg
        elif operator == "*":
            return leftarg * rightarg
        elif operator == "/":
            return float(leftarg) / rightarg
        elif operator == "//":
            return leftarg // rightarg
        elif operator == "%":
            return leftarg % rightarg
        elif operator == "**":
            return leftarg ** rightarg
        elif operator == "<":
            return int(leftarg < rightarg)
        elif operator == "<=":
            return int(leftarg <= rightarg)
        elif operator == "==":
            return int(leftarg == rightarg)
        elif operator == ">=":
            return int(leftarg >= rightarg)
        elif operator == ">":
            return int(leftarg > rightarg)
        elif operator in ("!=","<>"):
            return int(leftarg != rightarg)

    if operator == ".":
        # used to get attribute
        if isinstance(leftarg,dict):
            return leftarg.get(rightarg,"")
        # Make not list types to list
        if isinstance(leftarg,tuple):
            leftarg = list(leftarg)
        elif not isinstance(leftarg,list):
            leftarg = [leftarg]
        if isinstance(rightarg,tuple):
            rightarg = list(rightarg)
        elif not isinstance(rightarg,list):
            rightarg = [rightarg]
        # unary operator
        if leftarg == [None]:
            if rightarg == [None]: # no args at all
                return []
            return rightarg
        return leftarg+rightarg #return concatenated lists

    if operator == "@":
        if not isinstance(leftarg,(list,tuple)):
            leftarg = [leftarg]
        return [leftarg,rightarg]

    raise NotImplementedError("Operation '%s' is not implemented." %operator)

class TaskLayer():
    def __init__(self, task, parsed, envvar, tmpvar=None, stack=None, i=0):
        self.task = task
        self.parsedexpression = parsed
        self.envvar = envvar
        if stack == None:
            self.stack = []
        else:
            self.stack = stack
        if tmpvar == None:
            self.tmpvar = {}
        else:
            self.tmpvar = tmpvar
        self.i_max = len(self.parsedexpression)
        self.i = i
    def to_literal(self):
        return {"parsed":self.parsedexpression,
                "stack" :self.stack,
                "tmpvar":self.tmpvar,
                "i"     :self.i,
                }

class Task():
    def __init__(self, **args):
        self.finished = False
        self.result = None
        self.t_max = args.get("t_max",None)
        self.envvar = args.get("envvar",{})
        layers = args.get("layers",None)
        if layers != None:
            self.layers = [TaskLayer(self,envvar=self.envvar,**layer) for layer in layers]
        else:
            self.layers = [TaskLayer(self, parsed=args["parsed"], envvar=self.envvar)]
    
    def add_layer(self, parsedexpression,tmpvar=None):
        self.layers.append(TaskLayer(self,parsedexpression,self.envvar,tmpvar=tmpvar))

    def to_literal(self):
        return {"t_max":self.t_max,
                "envvar":self.envvar,
                "layers":[l.to_literal() for l in self.layers]}

class SyntaxTaggedString(unicode):
    def __init__(self,*args):
        unicode.__init__(self,*args)
        self.tags = []
    
    def add_tag(self,begin_index,end_index,tag):
        self.tags.append((begin_index,end_index,tag))

    def clear_tags(self):
        self.tags = []

    def get_tags(self):
        return self.tags

class Parser():
    OPERATOR_RANKING = [
            ':=', '+=','-=' , '*=', '/=', '%=', '**=',
            '<<', '<', '<=', '==', '>=', '>', '>>',
            '!=', '<>',
            '-', '+',
            '*', '/', '//', '%',
            '**',
            ':','!',
            '#',
            '@',
            '.',
            ]
    UNARY_OPERATOR_RANKING = OPERATOR_RANKING.index('#')
    UNARY_OPERATORS = ['-', '#', '.']

    ALLOWED_OPERATOR_CHARS = set("".join(OPERATOR_RANKING))
    
    def __init__(self):
        self.cache = {}
        self.filename = "<string>"

        self.READFUNCS = (
            (self._isNumber, self._readNumber),
            (self._isObjectName, self._readObjectName),
            (self._isOperator, self._readOperator),
            (self._isString, self._readString),
            (self._isUnit, self._readUnit),
            (self._isList, self._readList),
            (self._isStructure, self._readStructure),
            )

    def _isSubstring(self,expression,pos,string):
        return expression[pos:pos+len(string)] == string

    def _addTag(self,string,begin_index,end_index,tag):
        if isinstance(string,SyntaxTaggedString):
            string.add_tag(begin_index,end_index,tag)

    def _clearTags(self,string):
        if isinstance(string,SyntaxTaggedString):
            string.clear_tags()

    def _isNumber(self,char):
        return char.isdigit()

    def _readNumber(self,expression,pos):
        numberstring = ""
        maxpos = len(expression)
        begin_pos = pos
        while True:
            if pos >= maxpos:
                break
            char = expression[pos]
            if char.isdigit():
                numberstring += char
                pos += 1
            elif char == ".":
                if "." not in numberstring:
                    numberstring += char
                    pos += 1
                else:
                    break
            else:
                break
        self._addTag(expression,begin_pos,pos,"Number")
        if "." in numberstring:
            return [("write",float(numberstring))],pos
        return [("write",int(numberstring))], pos

    def _isObjectName(self,char):
        return char.isalpha()

    def _readObjectName(self,expression,pos):
        name = ""
        maxpos = len(expression)
        begin_pos = pos
        while True:
            if pos >= maxpos:
                break
            char = expression[pos]
            if char.isalnum() or (char in ('_')):
                name += char
                pos += 1
            else:
                break
        self._addTag(expression,begin_pos,pos,"ObjectName")
        return [("write",name)], pos

    def _isOperator(self,char):
        return char in self.ALLOWED_OPERATOR_CHARS

    def _readOperator(self,expression,pos):
        operator = ""
        maxpos = len(expression)
        begin_pos = pos
        space_flag = False
        while True:
            if pos >= maxpos:
                self._addTag(expression,begin_pos,pos,"Operator")
                raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
            char = expression[pos]
            if char in self.ALLOWED_OPERATOR_CHARS:
                if (operator in self.OPERATOR_RANKING) and (operator+char not in self.OPERATOR_RANKING):
                    break
                operator += char
                pos += 1
            else:
                break
        if operator not in self.OPERATOR_RANKING:
            raise SyntaxError("unknown operator %s" %operator,(self.filename,1,begin_pos,expression))
        self._addTag(expression,begin_pos,pos,"Operator")
        while True:
            if pos >= maxpos:
                raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
            char = expression[pos]
            if char == " ":
                pos += 1
            else:
                break
        return [("operator",operator)], pos

    def _isString(self,char):
        return char == "\""

    def _readString(self,expression,pos):
        string = ""
        maxpos = len(expression)
        begin_pos = pos
        while True:
            pos += 1
            if pos >= maxpos:
                self._addTag(expression,begin_pos,pos,"String")
                raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
            char = expression[pos]
            if char == "\\":
                pos += 1
                string += expression[pos:pos+1] #reads char at pos, but does not raise exception when pos is too high - maybe just use a try here
            elif char == "\"":
                break
            else:
                string += char
        self._addTag(expression,begin_pos,pos+1,"String")
        return [("write",string)], pos+1

    def _isUnit(self,char):
        return char == "("
    
    def _readUnit(self,expression,pos):
        # subexpression parsen
        self._addTag(expression,pos,pos+1,"Unit")
        parsedPart, pos = self._parse(expression,pos+1)
        if pos >= len(expression):
            #self._addTag(expression,begin_pos,pos,"String")
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if expression[pos] != ")":
            raise SyntaxError("expected ')'",(self.filename,1,pos,expression))
        self._addTag(expression,pos,pos+1,"Unit")
        return [parsedPart], pos + 1

    def _isList(self,char):
        return char == "["

    def _readList(self,expression,pos):
        self._addTag(expression,pos,pos+1,"List")
        pos += 1
        count = 0
        parsedList = []
        if expression != "]":
            while True:
                if pos == len(expression):
                    raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
                if expression[pos] == "]":
                    break
                parsedPart, pos = self._parse(expression,pos)
                parsedList.append(parsedPart)
                count += 1
                if pos == len(expression):
                    raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
                if expression[pos] == "]":
                    break
                if expression[pos] != ",":
                    raise SyntaxError("expected ',' od ']'",(self.filename,1,pos,expression))
                self._addTag(expression,pos,pos+1,"List")
                pos += 1
        self._addTag(expression,pos,pos+1,"List")
        #packaufruf anhängen
        parsedList.append(("pack",count))
        return [parsedList], pos + 1

    def _isStructure(self,char):
        return char == "{"

    def _readStructure(self,expression,pos):
        begin_pos = pos
        pos += 1
        if self._isSubstring(expression,pos,"foreach"):
            pos += 7
            raise NotImplementedError("\"foreach\" is not implemented yet")
        elif self._isSubstring(expression,pos,"while"):
            pos += 5
            self._addTag(expression,begin_pos,pos,"Structure")
            result, pos = self._readWhile(expression,pos)
        elif self._isSubstring(expression,pos,"until"):
            pos += 5
            self._addTag(expression,begin_pos,pos,"Structure")
            result,pos = self._readUntil(expression,pos)
        else: #erst mal if annehmen
            if self._isSubstring(expression,pos,"if"):
                pos += 2
            elif self._isSubstring(expression,pos,"case"):
                pos += 4
            else: #Fehler werfen, wenn es kein if ist
                raise SyntaxError("unknown structure type",(self.filename,1,pos,expression))
            self._addTag(expression,begin_pos,pos,"Structure")
            result,pos = self._readBranching(expression,pos)
        self._addTag(expression,pos-1,pos,"Structure")
        return result, pos

    def _readBranching(self,expression,pos):
        condition, pos = self._parse(expression,pos)
        branches = []
        maxpos = len(expression)
        if pos >= maxpos:
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        while expression[pos] != "}":
            if expression[pos] != ";":
                raise SyntaxError("expected ';' or '}'",(self.filename,1,pos,expression))
            self._addTag(expression,pos,pos+1,"Structure")
            branch, pos = self._parse(expression,pos+1)
            branches.append(branch)
            if pos >= maxpos:
                raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if len(branches) < 2:
            raise SyntaxError("did not expect '}' yet",(self.filename,1,pos,expression))
        parsedPart = []
        count = 0
        backwardPositions = []
        for branch in branches[::-1]:
            parsedPart.insert(0,branch)
            count += len(branch)+1
            backwardPositions.insert(0,count)
            parsedPart.insert(0,("jump",count))
        parsedPart.pop(0)
        parsedPart.insert(0,("case",[count+1-i for i in backwardPositions]))
        parsedPart.insert(0,condition)
        return [parsedPart], pos+1

    def _readWhile(self,expression,pos):
        condition,pos = self._parse(expression,pos)
        maxpos = len(expression)
        if pos >= maxpos:
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if expression[pos] != ";":
            raise SyntaxError("expected ';'",(self.filename,1,pos,expression))
        self._addTag(expression,pos,pos+1,"Structure")
        expPart, pos = self._parse(expression,pos+1)
        if pos >= maxpos:
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if expression[pos] != "}":
            raise SyntaxError("expected '}'",(self.filename,1,pos,expression))
        parsedPart = [("pack",0),condition,("if0jump",len(expPart)+4),expPart,
                      ("pack",1),("operator","."),("jump",-(len(expPart)+len(condition)+3))]
        return [parsedPart], pos+1

    def _readUntil(self,expression,pos):
        condition,pos = self._parse(expression,pos)
        maxpos = len(expression)
        if pos >= maxpos:
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if expression[pos] != ";":
            raise SyntaxError("expected ';'",(self.filename,1,pos,expression))
        self._addTag(expression,pos,pos+1,"Structure")
        expPart, pos = self._parse(expression,pos+1)
        maxpos = len(expression)
        if pos >= maxpos:
            raise SyntaxError("unexpected EOL",(self.filename,1,pos,expression))
        if expression[pos] != "}":
            raise SyntaxError("expected '}'",(self.filename,1,pos,expression))
        parsedPart = [("pack",0),expPart,("pack",1),("operator","."),condition,
                      ("if0jump",-(len(expPart)+len(condition)+2))]
        return [parsedPart], pos+1

    def cached_parse(self,expression):
        """Like 'parse', but uses cache to be faster.
        Used by kroet Interpreter."""
        parsed = self.cache.get(expression,None)
        if parsed == None:
            parsed = self.parse(expression)
            self.cache[expression] = parsed
        return parsed

    def parse(self,expression):
        """Parses kroet expression.
        Creates syntax tags if expression is SyntaxTaggedString."""
        self._clearTags(expression)
        parsed, endpos = self._parse(expression)
        #if endpos != len(expression):
        if endpos < len(expression):
            if expression[endpos]==";":
                self._addTag(expression,endpos+1,len(expression),"Comment")
            else:
                raise SyntaxError("unexpected character '%s'" %expression[endpos],(self.filename,1,endpos,expression))
        parsed = tuple(parsed)
        return parsed

    def _parse(self,expression,pos=0):
        max_pos = len(expression)
        parsed = []
        insertwait = False
        if expression[pos:pos+3] == "...": # wait
            insertwait = True
            self._addTag(expression,pos,pos+3,"Wait")
            pos += 3
        while pos < max_pos:
            char = expression[pos]
            if char == " ":
                pos += 1
            elif char in [")",";",",","}","]"]:
                break
            else:
                for isbegin,read in self.READFUNCS:
                    if isbegin(expression[pos]):
                        parts, pos = read(expression,pos)
                        for part in parts:
                            parsed.append(part)
                        break
                else:
                    raise SyntaxError("unexpected character '%s'" %expression[pos],(self.filename,1,pos,expression))
 
        # empty expression returns empty string if not ending with ])
        if parsed == []:
            parsed.append(("write",""))
 
        # reorder operators by ranking-> create "data1, data2, operator" order
        output = []
        self._reorder(parsed,output,0) # afterwards parsedExpression is empty and output full
        # flatten output
        self.flatten(output)
        # insert wait command if expression started with "..."
        if insertwait:
            output.insert(0,("wait",None))
        #M# output = self.compress(output)

        return output, pos

    def _get_ranking(self,operator):
        if operator[0] == "operator":
            return self.OPERATOR_RANKING.index(operator[1])
        return 0

    def _reorder(self,l_input,l_output,ranking): # works inplace
        if not l_input:
            raise SyntaxError("failed to resolve operators")
        element = l_input.pop(0)
        if element[0] == "operator":
            if element[1] not in self.UNARY_OPERATORS:
                raise SyntaxError("'%s' cannot be used as unary operator" %element[1])
            self._reorder(l_input,l_output,self.UNARY_OPERATOR_RANKING)
            l_output.append(("unary operator",element[1])) # unary operator
        else:
            l_output.append(element) # operand
        while l_input and self._get_ranking(l_input[0])>=ranking:
            operator = l_input.pop(0)
            self._reorder(l_input,l_output,self._get_ranking(operator))
            l_output.append(operator) # binary operator
            if operator[0] != "operator":
                l_output.append(("custom operation",None))
        return

    def flatten(self,nestedList):
        """e.g. [[1],2,[3,[4]],5,(6,[7])] -> [1,2,3,4,5,(6,[7])]"""
        i = 0
        while i<len(nestedList):
            if type(nestedList[i]) == list:
                for element in nestedList.pop(i)[::-1]:
                    nestedList.insert(i,element)
            else:
                i+=1

    def compress(self,parsed): #M# 
        """not completed yet, not sure if I want to anyway
        should compress parsed kroet parts where only literals are included
        e.g. "(1+1)*3" -> "6" """
        c = 0 # number of literals in front
        for i in xrange(len(parsed)):
            if parsed[i][0] == "write":
                c += 1
            elif parsed[i][0] == "operation" and c >= 2:
                try:
                    result = calculate(parsed[i][1],parsed[i-2],parsed[i-1])
                except NotImplementedError:
                    c = 0
                else:
                    parsed.pop(i),parsed.pop(i-1),parsed.pop(i-2)
                    parsed.insert(i-2,("write",result))
                    c -= 2
        #M# etc.


if __name__ == "__main__":
    from consoleIO import colorama
    colorama.init()
    Fore = colorama.Fore
    Back = colorama.Back
    Style = colorama.Style

    from consoleIO import Getch
    getch = Getch()
    raw_input = getch.raw_input
    
    import sys
    
    def goto(x,y):
        return '\x1b[%d;%dH' % (y, x)

    def nprint(text): # unlike the normal print this won't insert any newline or space after text
        sys.stdout.write(text)
        sys.stdout.flush()

    MINX = 1
    MINY = 1
    dt = 0.01

    def clearscreen():
        # set color to white-on-black with normal brightness.
        nprint('%s' %Style.RESET_ALL)
        # clear screen
        nprint('\x1b[2J')
        # put cursor to top, left
        nprint(goto(MINX, MINY))

    I = Interpreter()

    command1 = "1:[a:=5,{while #a;a:=#a-1}]"
    for command in (command1,):
        print "command:", command
        print "result: "+repr(I.execute(command,printstepinfo=False,stepbystep=False))
        import time
        for i in range(5):
            t = time.time()
            I.execute(command,printstepinfo=False,stepbystep=False)
            print "dt:",time.time()-t
    raw_input("---continue---")

    #command = "{while1;print:(int:[time:[]*10000]%10)}"
    #print "result: "+repr(I.execute(command,printstepinfo=False,stepbystep=False,tmax=0.1))
    #raw_input("---continue---")

    #FORES = [ Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.BLACK]
    COLORS = {"Number"     :Fore.MAGENTA,
              "ObjectName" :Fore.CYAN,
              "Wait"       :Fore.WHITE,
              "Operator"   :Fore.BLUE,
              "String"     :Fore.CYAN,
              "Unit"       :Fore.GREEN,
              "List"       :Fore.RED,
              "Structure"  :Fore.YELLOW,
              "Comment"    :Fore.WHITE,
              "error"      :Fore.RESET+Back.RED,
              }
    
    clearscreen()
    crode_history = [""]
    while True:
        crode = u""
        sequenz = []
        insertpos = 0
        clearscreen()
        nprint("%s>>> %s" %(Style.BRIGHT,Style.NORMAL))
        while True:
            time.sleep(dt)
            byte = getch()
            if byte:
                sequenz.append(byte)
            if sequenz:
                try:
                    char = bytearray(sequenz).decode(sys.stdin.encoding)
                except UnicodeDecodeError:
                    pass
                else:
                    sequenz = []
                    if ord(char) == 127: #Backspace
                        if insertpos > 0:
                            crode = crode[:insertpos-1]+crode[insertpos:]
                            insertpos -= 1
                    elif char == "\n":
                        try:
                            I.parser.parse(crode)
                        except:
                            pass
                        else:
                            break
                    elif char == u"\x1b": #Escape sequences, especially Arrow Keys
                        direction = []
                        while True:
                            c = getch()
                            if c == "":
                                break
                            direction.append(c)
                        if direction == ["[","D"]:
                            if insertpos > 0: #move cursor to the left
                                insertpos -= 1
                        elif direction == ["[","C"]: #move cursor to the right
                            if insertpos < len(crode):
                                insertpos += 1
                        elif direction == ["[","A"]: #load last entry from history
                            crode = crode_history[-1]
                            insertpos = len(crode)
                        elif direction == ["[","3","~"]: #delete
                            if insertpos < len(crode):
                                crode = crode[:insertpos]+crode[insertpos+1:]
                        else:
                            print "unknown key",direction
                            time.sleep(0.5)
                    else:#if 32<=ord(char)<127:
                        crode = crode[:insertpos]+char+crode[insertpos:]
                        insertpos += len(char)
                    clearscreen()
                    nprint("%s>>> %s" %(Style.BRIGHT,Style.NORMAL))
                    colored_crode = crode
                    tagged_line = SyntaxTaggedString(crode)
                    try:
                        I.parser.parse(tagged_line)
                    except SyntaxError as error:
                        nprint(" "*len(crode)+"\n\n") #leave space above for colored crode command
                        nprint(error.msg)
                        nprint(goto(MINX+4,MINY))
                        error_begin = max(error.offset,0) #error.offset can be None
                        tagged_line.add_tag(error_begin,len(crode),"error")
                    tags = [(tag_begin,COLORS.get(tag,"")) for tag_begin,tag_end,tag in tagged_line.get_tags()]
                    tags.append((insertpos,"\x1b[s")) #store curser pos
                    tags.sort(reverse=True)
                    for begin_index,color in tags:
                        colored_crode=colored_crode[:begin_index]+color+colored_crode[begin_index:]
                    nprint(colored_crode)
                    nprint("\x1b[u") #restore cursor pos
                    nprint(Style.RESET_ALL)
        if crode == "q":
            break
        elif crode == "":
            print I.filehandler.data
            print I.interrupted_funcs
            try:
                I.continue_execute()
            except:
                print "ERROR:",sys.exc_info()[1]
        else:
            crode_history.append(crode)
            try:
                print
                print "RESULT: "+repr(I.execute(crode,tmax=1,printstepinfo=False,stepbystep=True))
            except:
                #raise
                print "ERROR:",sys.exc_info()[1]
        print I.filehandler.data
        raw_input("---continue---")

    clearscreen()
    getch.close()
    colorama.deinit()