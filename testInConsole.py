
"""
Run GAEUnit tests in console
Adapted from http://code.google.com/p/gaeunit/wiki/Readme

Run all unit tests in test folder:
> python testInConsole.py

Run a single test module:
> python testInConsole.py testImport

"""

import urllib
import sys

if len(sys.argv) > 1:
    module = sys.argv[1]
else:
    module = None

# To run a specific test module, class, or method:
# * http://localhost:8080/test?name=test_module
# * http://localhost:8080/test?name=test_module.ClassTest
# * http://localhost:8080/test?name=test_module.ClassTest.testMethod 

baseurl = 'http://localhost:8080/test'

if module:
    url = '%s?name=%s&format=plain' % (baseurl, module)
else:
    url = '%s?format=plain' % baseurl

# can't just print the results
for line in urllib.urlopen(url):
    print line,

#ret = 0
#for line in urllib.urlopen('http://localhost:8080/test?format=plain'):
#for line in urllib.urlopen(url):
#    print line,
#    if 'FAILED (' in line:
#        ret = 1
# this works, but causes make to stop before it can display the results.        
#sys.exit(ret)

