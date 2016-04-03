import platform,sys,os
class Getch():
    """
    Gets single characters from standard input.
    Blocks normal input/raw_input. Use Getch.raw_input instead.
    """
    def __init__(self):
        self.system = platform.system()
        if self.system == "Windows":
            import msvcrt
            self.msvcrt = msvcrt
        elif self.system == "Linux":
            import tty
            self.tty = tty
            import select
            self.select = select
            try:
                import termios
            except ImportError:
                import TERMIOS as termios
            self.termios = termios
            self.old_settings = self.termios.tcgetattr(sys.stdin)
            self.tty.setcbreak(sys.stdin.fileno())            
            #self.tty.setraw(sys.stdin.fileno())
        else:
            print "unknown system",self.system
            print "won't be able to catch input"

    def __call__(self):
        if self.system == "Linux":
            try:
                if self.select.select([sys.stdin, ], [], [], 0)[0]:
                    char = os.read(sys.stdin.fileno(), 1)  # sys.stdin.read(1)
                    return char if type(char) is str else char.decode()
            except:
                print "unexpected error"
        elif self.system == "Windows":
            x = self.msvcrt.kbhit()
            if x:
                return self.msvcrt.getch()
        return ""

    def raw_input(self,quest):
        self.close()
        x = raw_input(quest)
        self.__init__()
        return x

    def close(self):
        self.termios.tcsetattr(sys.stdin, self.termios.TCSADRAIN, self.old_settings)
