import os
import time
import ConfigParser
import StandartCommands
reload(StandartCommands)

class Interpreter():
    def __init__(self,varset_func = None,objdir = None):
        self.objects = {}
        self.objecttypes = {}
        self.splitcache = {",":{},".":{},"=":{}}
        self.configparser = ConfigParser.ConfigParser()
        self.staticobjparser = ConfigParser.ConfigParser()
        self.staticobjfile = None
        self.filename = None
        self.envvar = []
        self.varset_func = varset_func
        self.objdir = objdir
        if self.objdir == None:
            import os
            self.objdir = "."+os.sep
        self.AdditionalCommandsets = []

    def open(self,filename,defaultfilename):
        if self.configparser.read(filename) == []:
            print "reading default file instead of savefile"
            if self.configparser.read(defaultfilename) == []:
                print "failed reading default file"
        self.filename = filename
        # Listen einrichten für type und landschaft

    def loadobject(self,objectname):
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
        for d in self.splitcache.values():
            d.clear()

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

    def get_attribute(self,objekt,attribute,default="",usetypeaction=True):
        if not self.objects.has_key(objekt):
            if not self.loadobject(objekt):
                return default
        if self.objects[objekt] == None:
            return default
        ret = self.objects[objekt].get(attribute,"")
        if ret in [""]:
            if self.objects[objekt].has_key("inherit"):
                return self.get_attribute(self.objects[objekt]["inherit"],attribute)
            return default
        return ret

    def set_attribute(self,objekt,attribute,value):
        if not self.objects.has_key(objekt):
            self.loadobject(objekt)
        if self.varset_func != None:
            valueold = self.get_attribute(objekt,attribute)
            self.varset_func(objekt,attribute,valueold,value)
        self.objects[objekt][attribute] = value

    def getlistattr(self,objekt,attribute,index):
        pass

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

    def create_object(self,name):
        if not self.objects.has_key(name):
            self.objects[name] = {}
        else:
            print "Error: object name %s already in use" %name
            return False

    def delete_object(self,name):
        if self.objects.has_key(name):
            self.objects[name] = None

    def split(self,string,char=","):
        """Do not modify resulting list inplace!!!"""
        if not self.splitcache[char].has_key(string):
            self._split(string,char)
        return self.splitcache[char][string]

    def _split(self,string,char):
        #string = string+"" #wozu ist diese Zeile da?
        if char not in string:
            self.splitcache[char][string] = [string]
            return
        b = []; lastindex = 0
        index = string.find(char)
        while index != -1:
            if (string.count('(',lastindex,index) ==
                string.count(')',lastindex,index)): #same for [] and {}
               #(string.count('"',lastindex,index)%2 == 0):
                b.append(string[lastindex:index])
                lastindex = index+1
            index = string.find(char,index+1)
        b.append(string[lastindex:])#+1 / +(lastindex!=0)
        self.splitcache[char][string] = b
        
    def list2str(self,l):
        r = "".join([str(i)+"," for i in l])
        if r.endswith(","):
            r = r[:-1]
        return r

    def execute(self,command,envvar=None,p=False):
        if envvar == None:
            envvar = {}
        if p:
            envvar["print"] = True
            p = False
        if envvar.get("print",False):
            print "command:",command
        try:
            #String
            if command.startswith("\\"):
                if command[1] == "(" and command[-1] == ")":
                    return command[2:-1]
                return command[1:]
            #Shortcuts
            command = StandartCommands.shortcuts.get(command,command)
            #Numbers
            split = self.split(command,".")
            if split[0].isdigit():
                if len(split) == 1:
                    return int(command)
                if len(split) == 2 and split[1].isdigit():
                    return float(command)
                return command
            #Attributes
            elif len(split)!=1:
                objexpr="".join(split[:-1])
                obj=self.execute(objexpr,envvar)
                attr=split[-1]
                return self.get_attribute(obj,attr)
            #Comparison
            split = self.split(command,"=")
            if len(split)!=1:
                return StandartCommands.isequal((self,envvar),
                            *[self.execute(j,envvar) for j in split])
            #Everything not yet proofed except functions
            i = command.find("(")
            if i == -1:
                return command
            #Function calls
            func = command[:i]
            args = self.split(command[i+1:-1])
            if args == [""]:
                args = []
            if StandartCommands.branch.has_key(func):
                branch = StandartCommands.branch[func]
                return branch((self,envvar),*args)
            else:
                args = [self.execute(j,envvar) for j in args]
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
        except:
            print "Error executing:", command
            raise

    def new_execute(self,command,envvar={}):
        if envvar.get("print",False):
            print "command:",command
        envvar["wait"] = False
        funcstack = [[[""]]] # of ["name",arg1,arg2,...,[argn1,operator1,argn2,operator2,...]]
        isstring = False
        escaped = False
        try:
            for letter in command:
                if escaped:
                    funcstack[-1][-1][-1]+=letter
                    escaped = False
                elif letter == "\\":
                    escaped = True
                elif letter == '"':
                    isstring = not isstring
                elif isstring:
                    funcstack[-1][-1][-1]+=letter
                else:
                    if letter in (" ",",",")"):
                        pass
                    if letter == "(":
                        funcstack.append([""])
                    elif letter == ",":
                        "sachen wie strings, numbers, = oder . auswerten"
                        funcstack[-1].append("")
                    elif letter == ")":
                        args = funcstack.pop(-1)
                        name = funcstack[-1].pop(-1)
                        result=self.call_function(name,args)
                        funcstack[-1].append(result)
                    elif letter in "=<>":
                        if letter == "=":
                            "testen ob letzter Buchstabe davon in !,<,> war"
                    elif letter in ".":
                        pass
                    else:
                        funcstack[-1][-1][-1]+=letter
                """( -> argumente fangen an (neue function in funcstack)
                , -> nächstes Argument (letzte function ausführen, neue anhängen)
                ) -> letzten 2 functionen ausführen
                = -> davor und danach vergleichen -> vergleichsfunktion anhängen
                . -> attributefunktion anhängen"""
                if envvar["wait"]:
                    "neuen command string aus funcstack erstellen"
                    break
                print funcstack
            return funcstack[0][0]
            #String
            if command.startswith("\\"):
                if command[1] == "(" and command[-1] == ")":
                    return command[2:-1]
                return command[1:]
            #Shortcuts
            command = StandartCommands.shortcuts.get(command,command)
            #Numbers
            split = self.split(command,".")
            if split[0].isdigit():
                if len(split) == 1:
                    return int(command)
                if len(split) == 2 and split[1].isdigit():
                    return float(command)
                return command
            #Attributes
            elif len(split)!=1:
                objexpr="".join(split[:-1])
                obj=self.execute(objexpr,envvar)
                attr=split[-1]
                return self.get_attribute(obj,attr)
            #Comparison
            split = self.split(command,"=")
            if len(split)!=1:
                return StandartCommands.isequal((self,envvar),
                            *[self.execute(j,envvar) for j in split])
            #Everything not yet proofed except functions
            i = command.find("(")
            if i == -1:
                return command
        except:
            print "Error executing:", command
            raise

    def solve_term(self,argsnops):
        arg1 = argsnops.pop(0)
        op   = None
        for i in argsnops:
            if op == None:
                op = i
            else:
                arg1 = call_function(op,(arg1,i))
                op = None

    def call_function(self,func,args):
        if args == []:
            return func
        else:
            return "".join(args)

        if StandartCommands.branch.has_key(func):
            branch = StandartCommands.branch[func]
            return branch((self,envvar),*args)
        else:
            #args = [self.execute(j,envvar) for j in args]
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


if __name__ == "__main__":
    I = Interpreter()
    #print I.split("test1")
    #print I.split("test2(bla,bli,blub)")
    #print I.split("var(envvar(\object),\position)")
    #print I.split("")
    #I.new_execute('mul(3,2,mul(4,5))')
    #I.new_execute('mul(2,3)=mul(3,2)')
    #tmpoffsetfunc(var(envvar(\object),\position))

def _parse(string):
    print string
    parsed = []
    functionstack = [["main",0]] #name,number of args
    operationstack = [None]
    tmp = ""
    addliteral = None
    currenttype = "expression" # of "operation","expression","string","escaped","number","float","object"
    string += " "
    for i in range(len(string)):
        char = string[i]
        if currenttype.startswith("wait"):
            currenttype = currenttype[4:]
        if currenttype == "object":
            if char.isalpha() or char.isdigit() or (char == "_"):
                tmp += char
            elif char == "(":
                functionstack.append([tmp,0])
                operationstack.append(None)
                tmp = ""
                currenttype = "expression"
            elif char == "{":
                if tmp in ("until",):
                    functionstack.append(["block",0])
                    parsed.append(("blockstart",tmp))
                    tmp = ""
                    currenttype = "waitexpression"
                else:
                    BaseException("Error parsing >"+string+"< at "+str(i)+": there is no structure named >"+tmp+"<")
            elif char == ".":
                tmp += char
            else:
                if "." in tmp:
                    pass #add varname and function for reading var to parsed
                raise BaseException("Error parsing >"+string+"< at "+str(i)+": unexpected character >"+char+"<")
        elif currenttype == "number":
            if char == ".":
                tmp += char
                currenttype = "float"
            elif char.isdigit():
                tmp += char
            else:
                addliteral = int(tmp)
                currenttype = "operation"
        elif currenttype == "float":
            if char.isdigit():
                tmp += char
            else:
                addliteral = float(tmp)
                currenttype = "operation"
        elif currenttype == "string":
            if char == '"':
                addliteral = tmp
                currenttype = "waitoperation"
            else:
                tmp += char
        elif currenttype == "escaped":
            tmp += char
            currenttype = "string"

        if addliteral != None:
            parsed.append(("write",addliteral))
            functionstack[-1][1]+=1
            tmp = ""
            if operationstack[-1] != None:
                parsed.append(("execute",(operationstack[-1],2)))
                functionstack[-1][1]-=1
                operationstack[-1] = None
            addliteral = None

        if currenttype == "operation":
            if char == "=":
                operationstack[-1] = char
                currenttype = "expression"
            elif char not in (" ",",",")","{","}",";"):
                if operationstack[-1] == None:
                    operationstack[-1] = ""
                operationstack[-1] += char
            if (char == " ") and (operationstack[-1] != None):
                currenttype = "expression"
        if currenttype == "expression":
            if char == '"':
                currenttype = "string"
            elif char.isdigit():
                currenttype = "number"
                tmp += char
            elif char.isalpha():
                tmp += char
                currenttype = "object"
        if currenttype in ("expression","operation"):
            if char == ")":
                if operationstack[-1] != None:
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": incomplete operation >"+operationstack[-1]+"<")
                if len(functionstack) == 1:
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": too much )")
                operationstack.pop(-1)
                funcname,argcount = functionstack.pop(-1)
                if funcname == "block":
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": too much ) in case")
                parsed.append(("execute",(funcname,argcount)))
                functionstack[-1][1]+=1
                if operationstack[-1] != None:
                    parsed.append(("execute",(operationstack[-1],2)))
                    functionstack[-1][1]-=1
                    operationstack[-1] = None
                tmp = ""
                currenttype = "operation"
            if char == ",":
                if operationstack[-1] != None:
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": incomplete operation >"+operationstack[-1]+"<")
                tmp = ""
                currenttype = "expression"
            if char == "{":
                if operationstack[-1] != None:
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": incomplete operation >"+operationstack[-1]+"<")
                functionstack[-1][1]-=1
                functionstack.append(["block",0])
                parsed.append(("blockstart","case"))
                tmp = ""
                currenttype = "expression"
            if char in ("}",";"):
                funcname,argcount = functionstack[-1]
                if funcname != "block":
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": missing )")
                if argcount != 1:
                    print argcount,operationstack,functionstack,parsed
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": bad block (one value, no commata expected)")
                if operationstack[-1] != None:
                    raise BaseException("Error parsing >"+string+"< at "+str(i)+": incomplete operation >"+operationstack[-1]+"<")
                tmp = ""
                currenttype = "expression"
            if char == "}":
                functionstack.pop(-1)
                parsed.append(("blockend",None))
                functionstack[-1][1]+=1
            if char == ";":
                functionstack[-1][1]=0
                parsed.append(("blockdiv",None))

    if currenttype not in ("expression","operation"):
        raise BaseException("Error parsing >"+string+"<: missing end of "+currenttype)
    if operationstack[-1] != None:
        raise BaseException("Error parsing >"+string+"<: incomplete operation >"+operationstack[-1]+"<")
    if operationstack != [None]:
        raise BaseException("Error parsing >"+string+"<: unexpected end of command")
    if functionstack[-1][1] != 1:
        print functionstack
        raise BaseException("Error parsing >"+string+"<: bad block (one value, no commata expected)")
    if functionstack != [["main",1]]:
        raise BaseException("Error parsing >"+string+"<: unknown error")

    i = 0
    state = 0
    i_blockdivs = []
    i_blockend = None
    while i < len(parsed):
        if state == 0:
            if parsed[i][0]=="blockend":
                parsed[i]=(None,None)
                i_blockend = i
                state = 1
            else:
                i += 1
        elif state == 1:
            if parsed[i][0]=="blockdiv":
                i_blockdivs.insert(0,i)
            if parsed[i][0]=="blockstart":
                if parsed[i][1]=="case":
                    goto = [i_blockdivs[-1]+1,i+1]
                    for i_blockdiv in i_blockdivs:
                        goto.append(i_blockdiv+1)
                        parsed[i_blockdiv]=("goto",i_blockend)
                    goto.pop(-1)
                    parsed[i]=("case",goto)
                elif parsed[i][1]=="until":
                    #M#
                    if len(i_blockdivs)!=0:
                        raise BaseException("Error parsing >"+string+"< at "+str(i)+": bad until block")
                    parsed[i]=(None,None)
                    parsed[i_blockend]=("gotoifzero",i)
                    pass
                i_blockdivs = []
                i_blockend = None
                state = 0
            else:
                i -= 1

    return parsed

class Parser():
    def __init__(self):
        self.cache = {}

        self.readfuncs = [
            (self.isNumber, self.readNumber),
            (self.isObjectName, self.readObjectName),
            (self.isOperator, self.readOperator),
            (self.isString, self.readString),
            (self.isUnit, self.readUnit),
            (self.isList, self.readList),
            (self.isStructure, self.readStructure),
            ]

        self.operatorRanking = [
            ':=',
            '<<', '<', '<=', '==', '>=', '>', ">>",
            '!=', '<>',
            '-', '+',
            '/', '*',
            '**',
            ':',
            '.',
            ]
        self.allowedChars = set("".join(self.operatorRanking))

    def isSubstring(self,expression,pos,string):
        return expression[pos:pos+len(string)] == string

    def isNumber(self,char):
        return char.isdigit()

    def readNumber(self,expression,pos):
        numberstring = ""
        maxpos = len(expression)
        while True:
            if pos >= maxpos:
                break
            char = expression[pos]
            if char.isdigit() or (char == "."):
                numberstring += char
                pos += 1
            else:
                break
        if "." in numberstring:
            return ("write",float(numberstring)),pos
        return ("write",int(numberstring)), pos

    def isObjectName(self,char):
        return char.isalpha()

    def readObjectName(self,expression,pos):
        name = ""
        maxpos = len(expression)
        while True:
            if pos >= maxpos:
                break
            char = expression[pos]
            if char.isalnum() or (char == "_"):
                name += char
                pos += 1
            else:
                break
        return ("write",name), pos

    def isOperator(self,char):
        return char in self.allowedChars

    def readOperator(self,expression,pos):
        operator = ""
        maxpos = len(expression)
        while True:
            if pos >= maxpos:
                raise BaseException("Error parsing >%s<: unexpected EOL" %expression)
            char = expression[pos]
            if char in self.allowedChars:
                operator += char
                pos += 1
            else:
                break
        if operator in self.operatorRanking:
            return ("operator",operator), pos
        else:
            raise BaseException("Error parsing >%s< at %i: unknown Operator %s" %(expression,pos,operator))

    def isString(self,char):
        return char == "\""

    def readString(self,expression,pos):
        string = ""
        maxpos = len(expression)
        while True:
            if pos >= maxpos:
                raise BaseException("Error parsing >%s<: unexpected EOL" %expression)
            pos += 1
            char = expression[pos]
            if char == "\\":
                pos += 1
                string += expression[pos]
            if char == "\"":
                break
            else:
                string += char
        return ("write",string), pos+1

    def isUnit(self,char):
        return char == "("
    
    def readUnit(self,expression,pos):
        # subexpression parsen
        parsedPart, pos = self._parse(expression,pos+1)
        if expression[pos] != ")":
            raise BaseException("Error parsing >%s< at %i: expected ')'" %(expression,pos))
        return parsedPart, pos + 1

    def isList(self,char):
        return char == "["

    def readList(self,expression,pos):
        pos += 1
        count = 0
        parsedList = []
        while expression[pos] != "]":
            parsedPart, pos = self._parse(expression,pos)
            parsedList.append(parsedPart)
            count += 1
            if expression[pos] == "]":
                break
            if expression[pos] != ",":
                raise BaseException("Error parsing >%s< at %i: expected ',' or ']'" %(expression,pos))
            pos += 1
        #packaufruf anhängen
        parsedList.append(("pack",count))
        return parsedList, pos + 1

    def isStructure(self,char):
        return char == "{"

    def readStructure(self,expression,pos):
        pos += 1
        if self.isSubstring(expression,pos,"foreach"):
            pos += 7
            raise NotImplementedError("\"foreach\" is not implemented yet")
        elif self.isSubstring(expression,pos,"while"):
            pos += 5
            return self.readWhile(expression,pos)
        elif self.isSubstring(expression,pos,"until"):
            pos += 5
            return self.readUntil(expression,pos)
        else: #erst mal if annehmen
            if self.isSubstring(expression,pos,"if"):
                pos += 2
            elif self.isSubstring(expression,pos,"case"):
                pos += 4
            else: #Fehler werfen, wenn es kein if ist
                raise BaseException("Error parsing >%s<: unknown structure type" %expression)
            return self.readBranching(expression,pos)

    def readBranching(self,expression,pos):
        condition, pos = self._parse(expression,pos)
        branches = []
        while expression[pos] != "}":
            if expression[pos] != ";":
                raise BaseException("Error parsing >%s< at %i: expected ';' or '}'" %(expression,pos))
            branch, pos = self._parse(expression,pos+1)
            branches.append(branch)
        if len(branches) < 2:
            raise BaseException("Error parsing >%s< at %i: did not expect '}' yet" %(expression,pos))
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
        return parsedPart, pos+1

    def readWhile(self,expression,pos):
        condition,pos = self._parse(expression,pos)
        if expression[pos] != ";":
            raise BaseException("Error parsing >%s< at %i: expected ';'" %(expression,pos))
        expPart, pos = self._parse(expression,pos+1)
        if expression[pos] != "}":
            raise BaseException("Error parsing >%s< at %i: expected '}'" %(expression,pos))
        parsedPart = [("pack",0),condition,("if0jump",len(expPart)+4),expPart,
                      ("pack",1),("operator","+"),("jump",-(len(expPart)+len(condition)+3))]
        return parsedPart, pos+1

    def readUntil(self,expression,pos):
        condition,pos = self._parse(expression,pos)
        if expression[pos] != ";":
            raise BaseException("Error parsing >%s< at %i: expected ';'" %(expression,pos))
        expPart, pos = self._parse(expression,pos+1)
        if expression[pos] != "}":
            raise BaseException("Error parsing >%s< at %i: expected '}'" %(expression,pos))
        parsedPart = [("pack",0),expPart,("pack",1),("operator","+"),condition,
                      ("if1jump",-(len(expPart)+len(condition)+2))]
        return parsedPart, pos+1

    def parse(self,expression):
        print expression
        parsed = self.cache.get(expression,None)
        if parsed == None:
            parsed,endpos = self._parse(expression,0)
            parsed = tuple(parsed)
            if endpos != len(expression):
                raise BaseException("Error parsing >%s< at %i: exited too early" %(expression,endpos))
            self.cache[expression] = parsed
        return parsed

    def _parse(self,expression,pos):
        max_pos = len(expression)
        parsed = []
        while pos < max_pos:
            char = expression[pos]
            if char == " ":
                pos += 1
            elif char in [")",";",",","}","]"]:
                break                    
            else:
                for isbegin,read in self.readfuncs:
                    if isbegin(expression[pos]):
                        part, pos = read(expression,pos)
                        parsed.append(part)
                        break
                else:
                    raise BaseException("Error parsing >%s< at %i: unexpected character" %(expression,pos))

        # Nach Wertigkeit der Operatoren ordnen
        if parsed == []:
            parsed.append(("write",""))
        self.sort(parsed)
        if len(parsed) != 1:
            raise BaseException("Error parsing >%s<: failed to resolve operators" %expression)

        parsed = self.flatten(parsed)

        return parsed, pos

    def sort(self,parsedExpression): #works inplace
        while True:
            best_r = -1
            best_i = None
            for i in xrange(len(parsedExpression)):
                part = parsedExpression[i]
                if part[0] == "operator":
                    if part[1] in self.operatorRanking:
                        r = self.operatorRanking.index(part[1])
                        if r > best_r:
                            best_r, best_i = r, i
            if best_i == None:
                break
            else:
                left = parsedExpression.pop(best_i-1)
                operation = parsedExpression.pop(best_i-1)
                right = parsedExpression.pop(best_i-1)
                parsedExpression.insert(best_i-1,[left,right,operation])
        while len(parsedExpression) >= 3:
            left = parsedExpression.pop(0)
            customoperation = parsedExpression.pop(0)
            right = parsedExpression.pop(0)
            parsedExpression.insert(0,[left,customoperation,right,("custom operation",None)])

    def flatten(self,nestedList):
        result = []
        for element in nestedList:
            if type(element) == list:
                result += self.flatten(element)
            else:
                result.append(element)
        return result


# Verzweigung
#     {if indexgenerator; ausdruck1; index=ausdruck0} #index ist boolscher Wert
# Mehrfachverzweigung
#     {case indexgenerator; ausdruck1; ausdruck2; ...; ausdruck_n; ausdruck_sonst} #index ist natürliche Zahl
## Kurzform für Verzweigungen:
##     {indexgenerator; index=1; ...; index=sonst}
# Kopfabweisende Schleife
#     {while bedingung; ausdruck} -> [Rückgabewerte von anweisung]
# Fußabweisende Schleife
#     {until bedingung; ausdruck}

## "Zählschleife"
##     {foreach Menge; anweisung} wobei :[element] an anweisung angehängt wird?

def _execute(parsedexpression, i=0, t_max=None):
    # write, operator, operation, pack, case, jump, if0jump
    stackedStacks = []
    stack = []
    i_max = len(parsedexpression)
    t = time.time()
    while (i < i_max) and (time.time()-t < t_max):
        action, parameter = parsedexpression[i]
        if action == "write":
            stack.append(parameter)
            i += 1
        if action == "pack":
            newlist = []
            for j in range(parameter):
                newlist.insert(0,stack.pop(-1))
            stack.append(newlist)
        elif action == "operator":
            operator = parameter
            argument_r = stack.pop(-1)
            argument_l = stack.pop(-1)
            # ausführen
            i += 1
        elif action == "custom operation":
            left = stack.pop(-1)
            customoperation = stack.pop(-1)
            right = stack.pop(-1)
            # ausführen
            i += 1
        elif action == "case":
            index = stack.pop(-1)
            if type(index) != int:
                raise TypeError("index in case structure must be of type integer")
            if 0 < index < len(parameter):
                i = parameter[index-1]
            else:
                i = parameter[-1]
        elif action == "jump":
            i = parameter
        elif action == "if0jump":
            condition = stack.pop(-1)
            if not bool(condition):
                i = parameter
            else:
                i += 1
        elif action == "if1jump":
            condition = stack.pop(-1)
            if bool(condition):
                i = parameter
            else:
                i += 1
        else:
            raise BaseException("Unknown action %s in parsed expression" %action)

if __name__ == "__main__":
    #print _parse('42')
    #print _parse('mul(2,3)')
    ##print _parse('2*(1+4)')
    #print _parse('mul(2,3)=mul(4,5)')
    #print _parse('mul(2,3)=mul("böse:), ",2 and 3)')
    #print _parse('0{1;until{1};3;0}')

    p = Parser()

    print p.parse('mul:[2,3]/6')

    print p.parse('3*(a+b)')

    print p.parse('3 random:["*","+"] 4+2') #Leerzeichen können sogar weggelassen werden, sieht aber blöd aus
    
    print p.parse('[a,c]:=a.b:[a.c,3]')
    
    print p.parse('{if a;b;c+1;d}')
    
    print p.parse('{until a;b}')