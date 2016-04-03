#* coding: utf-8 *#
# Einrückung, Parsen, Highlighting, Ausführen, Korrespondierende Klammern markieren

COLORS = {"Number"     :"purple",
          "ObjectName" :"gray5",
          "Dereference":"midnight blue",
          "Operator"   :"navy",
          "String"     :"gray25",
          "Unit"       :"blue",
          "List"       :"red",
          "Structure"  :"dark orange",
          "Comment"    :"gray50",
          }

try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

import sys
sys.path.append("..")
import kroet
reload(kroet)
Parser = kroet.Parser()

root = tk.Tk()
root.geometry("600x200")

class CustomText(tk.Text): #http://stackoverflow.com/questions/23571407/how-to-i-have-the-call-back-in-tkinter-when-i-change-the-current-insert-position
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lrange $args 0 2] == {mark set insert})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

def cursor_moved(*args):
    curline = edit.index(tk.INSERT).split(".")[0]
    for tag in edit.tag_names():
        if tag.startswith("fullline_error"):
            edit.tag_delete(tag)
    for tag in edit.tag_names():
        if tag.startswith("partline_error"):
            line = tag[14:]
            if line != curline:
                tagname = "fullline_error"+line
                end_index = "%s.0" %str(int(line)+1)
                begin_index = "%s.0" %line
                edit.tag_add(tagname, begin_index, end_index)
                edit.tag_config(tagname,background="pink")#,font="bold")
            

def text_changed(*args):
    if edit.edit_modified():
        edit.edit_modified(False)
        text = edit.get("1.0","end")
        pos = edit.index(tk.INSERT)
        for tag in edit.tag_names():
            edit.tag_delete(tag)

        for y, line in enumerate(text.split("\n")):
            line_index = "%s.0" %(y+1)
            tagged_line = kroet.SyntaxTaggedString(line)
            try:
                Parser.parse(tagged_line)
            except SyntaxError as error:
                c_begin = max(error.offset,0) #error.offset can be None
                tagname = "partline_error"+str(y+1)
                #if y == int(pos.split(".")[0])-1:
                begin_index = line_index+"+%sc" %c_begin
                #else:
                #    begin_index = line_index
                end_index = line_index+"+%sc" %len(tagged_line)
                edit.tag_add(tagname, begin_index, end_index)
                edit.tag_config(tagname,background="pink")#,font="bold")
            for c_begin, c_end, tag in tagged_line.get_tags():
                begin_index = line_index+"+%sc" %c_begin
                end_index = line_index+"+%sc" %c_end
                tagname = begin_index+":"+end_index
                #print begin_index, end_index
                edit.tag_add(tagname, begin_index, end_index)
                edit.tag_config(tagname, foreground=COLORS.get(tag,"black"))

edit = CustomText(root,undo=True,font="bold")
edit.pack(fill="both", expand=True)
edit.bind('<<Modified>>', text_changed)
edit.bind('<<Change>>', cursor_moved)

text = """1:[a:=5,{while #a;a:=#a-1}]
"Teststring"
[And,a,List,2*(3+4)]"""

edit.insert("end",text)

root.mainloop()