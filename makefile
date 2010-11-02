#---------------------------------------------------------------
# makefile for ASN project
# assumes that google_appengine is located in parent folder
#---------------------------------------------------------------

# need this because 'make test' doesn't work otherwise (?)
.PHONY: test



# need this for pydoc and pychecker
export PYTHONPATH := ../google_appengine/:../google_appengine/lib/webob

# need this for twill (web site testing)
export PYTHONPATH := ~/lib/python:${PYTHONPATH}



#pychecker := pychecker
# this is v0.8.16:
#pychecker := "/p/lib/python2.4/site-packages/pychecker/checker.py"
# installed v0.8.18 in my dirs:
pychecker := "/u/bburns/bin/pychecker-0.8.18/pychecker/checker.py"

# no good installation of pylint on cs machines. so do it ourselves
pylint := pylint

pydoc := pydoc
epydoc := /public/linux/graft/epydoc-2.1/bin/epydoc




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


# run the app locally
run:
	../google_appengine/dev_appserver.py .



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



# publish the app to google appengine
publish:
	../google_appengine/appcfg.py update .


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


# zip up files for turnin
zip:
	zip -r ASN2.zip ASN2.log test/*.py ASN2.py xmlImport.py xmlExport.py html


# do turnin
turnin:
	turnin --submit alexloh cs373pj6 ASN2.zip
	turnin --list alexloh cs373pj6
