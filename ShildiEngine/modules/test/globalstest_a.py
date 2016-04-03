DEBUG = False
import sys
if DEBUG:
    sys.argv.append("--debug")
print sys.argv
from globalstest_b import main
main()