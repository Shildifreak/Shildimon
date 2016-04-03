#File: Tkintermenus

from Tkinter import*
import tkMessageBox

def logindialog():
    global back
    """back:(name,passwort)"""
    fenst = Tk()
    def hole(wo=None):
        global back
        back = (e1.get(), e2.get())
        fenst.quit()
    def wechsel1(wo):
        e2.focus_set()
    def wechsel2(wo):
        b1.focus_set()
    def gibtsni():
        tkMessageBox.showinfo("HELP HELP","""there is no help
    es gibt keine Hilfe""")
    Label(fenst,text="Name    ").grid(row=1,column=0)
    Label(fenst,text="Passwort").grid(row=2,column=0)
    b1 = Button(fenst,text="Anmelden",command=hole)
    b1.grid(row=3, column=0)
    b2 = Button(fenst,text="Cancel",command=fenst.quit)
    b2.grid(row=3, column=1)
    b3 = Button(fenst,bitmap="questhead",command=gibtsni)
    b3.grid(row=3, column=2)
    e1 = Entry(fenst)
    e1.configure(background="white",foreground="blue")
    e1.grid(row=1,column=1,columnspan=2)
    e2 = Entry(fenst)
    e2.configure(background="white",foreground="white")
    e2.grid(row=2,column=1,columnspan=2)
    e1.bind("<Return>",wechsel1)
    e2.bind("<Return>",wechsel2)
    b1.bind("<Return>",hole)
    e1.focus_set()
    fenst.mainloop()
    fenst.destroy()
    if back in dir():
        back = ("","")
    return back

def askstring(title=None,question=""):
    global answer
    fenst = Tk()
    fenst.wm_title(title)
    L = Label(fenst, text=question)
    L.pack()
    E = Entry(fenst)
    E.configure(background="white")
    E.pack()
    def hole(wodummi=None):
        global answer
        answer = E.get()
        fenst.quit()
    E.bind("<Return>",hole)
    E.focus_set()
    fenst.mainloop()
    fenst.destroy()
    if answer in dir():
        answer = None
    return answer

if __name__ == "__main__":
    print logindialog()
    print
    print askstring("Title","???????????????")
