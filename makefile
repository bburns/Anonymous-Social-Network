#---------------------------------------------------------------
# makefile for ASN1 project
# assumes that google_appengine is located in parent folder
#---------------------------------------------------------------

# need this because 'make test' doesn't work otherwise (?)
.PHONY: test

# need this for pydoc and pychecker
export PYTHONPATH := ../google_appengine/:../google_appengine/lib/webob




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
# (app needs to be running locally)
test:
	python testInConsole.py > ASN1.out
	cat ASN1.out



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


# run the app locally
run:
	../google_appengine/dev_appserver.py .


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
	git log > ASN1.log
	cat ASN1.log


# generate html docs
docs:
#	pydoc ASN1
	rm -rf html
	mkdir html
	pydoc -w ASN1
	mv ASN1.html html


# epydoc
# it works, but it does make a LOT of files
edoc:
	${epydoc} --html -o html2 ASN1.py


# zip up files for turnin
zip:
	zip -r ASN1.zip ASN1.log test/*.py ASN1.py xmlImport.py xmlExport.py ASN1.xml ASN1.xsd ASN1.pdf html


# do turnin
turnin:
	turnin --submit alexloh cs373pj5 ASN1.zip
	turnin --list alexloh cs373pj5
