import sys

def main():
    if "--debug" in sys.argv:
        print "debug mode"
    else:
        print "no debug mode"