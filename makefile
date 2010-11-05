#---------------------------------------------------------------
# makefile for ASN project
# assumes that google_appengine is located in parent folder
#---------------------------------------------------------------

# need this because 'make test' doesn't work otherwise (?)
.PHONY: test


ifeq ($(OS),Windows_NT)
appserver := ..\google_appengine\dev_appserver.py

else
#pychecker := pychecker
# this is v0.8.16:
#pychecker := "/p/lib/python2.4/site-packages/pychecker/checker.py"
# installed v0.8.18 in my dirs:
pychecker := "/u/bburns/bin/pychecker-0.8.18/pychecker/checker.py"

# no good installation of pylint on cs machines. so do it ourselves
pylint := pylint

pydoc := pydoc
epydoc := /public/linux/graft/epydoc-2.1/bin/epydoc
appserver := ../google_appengine/dev_appserver.py
endif



# run the unit tests in the console
# (app needs to be running locally - do make run in another console)
# to test all modules, do
# > make test
# or 
# > make
# to test a single module, do something like this - 
# > make test name=testExport 
# it will call
# http://localhost:8080/test?name=<name>&format=plain
# default of no name will run all test modules
name := 
test:
	python testInConsole.py ${name} > ASN2.out
	cat ASN2.out


# run twill tests 
#. doesn't work from here yet - just run in shell
# (app needs to be running locally)
# runs all test scripts in the test/twill directory
# no output means everything passed
#. can also pass -u to twill to give it an initial url, 
# so could test locally or the server version
export PYTHONPATH := ~/lib/python
twill:
	twill-sh -q test/twill


# run the app locally
# by default gae puts the datastore in /tmp/dev_appserver.datastore
# may need to put it somewhere else with --datastore_path=~/myapp_datastore 
# that way your data will always be there
run:
#	../google_appengine/dev_appserver.py .
	$(appserver) --datastore_path=datastore .


# publish the app to google appengine
publish:
	../google_appengine/appcfg.py update .



# need this for pydoc and pychecker
export PYTHONPATH := ../google_appengine/:../google_appengine/lib/webob

# can do make pypath if you just need to set the PYTHONPATH environment variable,
# as it is set up above. this just prints it out. 
#. no, you can't - things set here don't make it into the calling environment. bleh. 
# how can you do that?
pypath:
	@echo PYTHONPATH := ${PYTHONPATH}


# check using pychecker
# 0.8.16 is installed on linux machines
# --only option was added in 0.8.17
# If there are import dependencies in your source files, you should import those files first on the command line in order to get as many files checked as possible.
# --only      only warn about files passed on command line
# --stdlib    ignore warnings from stdlib
# --blacklist ignore warnings from list of modules [['', '']]
check:
#	${pychecker} --blacklist "webapp" xmlImport.py xmlExport.py ASN1.py
#	python ${pychecker} --only ASN1.py
#	python ${pychecker} --only ASN1.py xmlImport.py xmlExport.py
	python ${pychecker} --only ASN1.py xmlImport.py xmlExport.py test/*.py
#	python ${pychecker} --only ASN1.py
#	python ${pychecker} --only xmlImport.py
#	python ${pychecker} --only xmlExport.py


#xml: xml/ben.xml xml/brian.xml xml/jonathan.xml xml/sang.xml xml/shanky.xml
#	cat xml/ben.xml xml/brian.xml xml/jonathan.xml xml/sang.xml xml/shanky.xml > ASN1.xml



# generate html docs
docs:
#	pydoc ASN2
	rm -rf html
	mkdir html
	pydoc -w ASN2
	mv ASN2.html html


# epydoc
# it works, but it does make a LOT of files
edoc:
	${epydoc} --html -o html2 ASN2.py



# validate xml against schema
#. not working from here
validate:
	cd xml
	validate *.xml
	cd ..


# get git log
log:
	git log > ASN2.log
	cat ASN2.log



# zip up files for turnin
zip:
	zip -r ASN2.zip ASN2.log test/*.py ASN2.py xmlImport.py xmlExport.py html


# do turnin
turnin:
	turnin --submit alexloh cs373pj6 ASN2.zip
	turnin --list alexloh cs373pj6
