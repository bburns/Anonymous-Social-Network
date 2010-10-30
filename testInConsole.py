
# Run GAEUnit tests in console
# From http://code.google.com/p/gaeunit/wiki/Readme


import urllib
import sys


# To run a specific test module, class, or method:
# * http://localhost:8080/test?name=test_module
# * http://localhost:8080/test?name=test_module.ClassTest
# * http://localhost:8080/test?name=test_module.ClassTest.testMethod 

#ret = 0
url = 'http://localhost:8080/test'
#module = 'testImport'
#format = 'plain'

if len(sys.argv) > 1:
    module = sys.argv[1]
else:
    module = None

if module:
    s = '%s?name=%s&format=plain' % (url, module)
else:
    s = '%s?format=plain' % url
#print module
#print s
#for line in urllib.urlopen('http://localhost:8080/test?format=plain'):
for line in urllib.urlopen(s):
    print line,
#    if 'FAILED (' in line:
#        ret = 1

# this works, but causes make to stop before it can display the results.        
#sys.exit(ret)

