
# Run GAEUnit tests in console
# From http://code.google.com/p/gaeunit/wiki/Readme


import urllib
import sys

#ret = 0
for line in urllib.urlopen('http://localhost:8080/test?format=plain'):
    print line,
#    if 'FAILED (' in line:
#        ret = 1

# this works, but causes make to stop before it can display the results.        
#sys.exit(ret)

