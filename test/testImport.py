#!/usr/bin/env python

# -------------------------------
# testImport.py
# Copyright (C) 2010
# Jonathan Grimes
# -------------------------------

# -------
# imports
# -------

import unittest
from google.appengine.ext import db
from models import *
from utils.xmlImport import *



# -----------
# TestImport
# -----------


class testImport (unittest.TestCase) :

    #. move this to utils
    def dbClear(self):
        "A helper method to clear the database"
        # query = Student.all()
        # db.delete(query)    

        # you actually have to clear the association tables also -
        # even if you delete all the related objects, the association objects
        # are still there!
        # which makes sense, as appengine doesn't know they're just association objects.
        tables = [Student, Class, Book, Paper, Internship, Place, Game]
        tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
        for table in tables:
            query = table.all()
            db.delete(query)


    def testImportStudent(self):

        self.dbClear()
        xmlImportString("<students><student><id>12345678</id><password>brian</password></student> </students>")
        query = Student.all()
        students = query.fetch(999)
        s = students[0]
        self.assert_(s.id_ == "12345678", s.id_)
        self.assert_(s.password == "brian", s.password)


    def testImportNothing(self):

        self.dbClear()
        xmlImportString("<students></students>")
        query = Student.all()
        students = query.fetch(999)
        self.assert_(len(students) == 0)


    #. fails - need to catch exception?
    # def testImportNothing2(self):
    #     self.dbClear()
    #     xmlImportString("")
    #     query = Student.all()
    #     students = query.fetch(999)
    #     self.assert_(len(students) == 0)


    def testImportStudentClass(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]
	sclist = student.studentclass_set.fetch(9857437)
	sc = sclist[0]
	c = sc.class_
	self.assert_(sc.rating == "95")
	self.assert_(sc.comment== "There were many new concepts")
	self.assert_(c.unique == "52540")
	sc2 = sclist[1]
	c2 = sc2.class_
	self.assert_(sc2.rating == "55")
	self.assert_(c2.course_name == "Linear Algebra")

    
    def testImportStudentClass3(self) :
        # try importing a string

        self.dbClear()
	xmlImportString('<students><student><class><unique>12345</unique><course_num>CS 343</course_num><course_name>AI</course_name><grade>A</grade><rating>93</rating><comment>cool</comment> </class></student></students>')
	query = Student.all()
	students = query.fetch(1)
	student = students[0]
	sclist = student.studentclass_set.fetch(1)
	sc = sclist[0]
	c = sc.class_
	self.assert_(c.unique == "12345")
	self.assert_(sc.grade == "A")
	self.assert_(sc.rating == "93")
	self.assert_(c.course_num == "CS 343")
	self.assert_(sc.comment == "cool")


    def testImportStudentClass2(self) :

        self.dbClear()
	#xmlImportFile('testImport.xml')
	xmlImportString('<students><student><class><id>foo</id><unique>12345</unique><course_num>CS 343</course_num><course_name>AI</course_name><grade>A</grade><rating>93</rating><comment></comment> </class><class><unique>54321</unique><grade>F</grade><comment>hard</comment></class></student></students>')
	query = Student.all()
	students = query.fetch(1)
	student = students[0]
	sclist = student.studentclass_set.fetch(2)
	sc = sclist[0]
	c = sc.class_
	self.assert_(c.unique == "12345")
	self.assert_(sc.grade == "A")
	sc2 = sclist[1]
	c2 = sc2.class_
	self.assert_(c2.unique == "54321")
	self.assert_(sc2.grade == "F")
	self.assert_(sc2.comment == "hard")


    def testImportStudentBook(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	sblist = student.studentbook_set.fetch(9857437)
	
	#test 1 Book			
	sb = sblist[0]
	b = sb.book
	self.assert_(sb.rating == "97")
	self.assert_(sb.comment == "Long")
	self.assert_(b.isbn == "4356745290")
	self.assert_(b.title == "Automata, Complexity, and Computability", b.title)
	self.assert_(b.author == "Elaine Rich")
	
	#test 2 books
	sb = sblist[1]
	b = sb.book
	self.assert_(sb.rating == "90")
	self.assert_(b.isbn == "0679736646")
	self.assert_(b.title == "Test", b.title)
	self.assert_(b.author == "Ben Kornfuehrer")


    def testImportStudentBook2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[1]	
	sblist = student.studentbook_set.fetch(9857437)
	
	#test 1 Book		
	
	sb = sblist[0]
	b = sb.book
	self.assert_(sb.rating == "95")
	self.assert_(sb.comment == "crazy")
	self.assert_(b.isbn == "0679734465")
	self.assert_(b.title == "Valis", b.title)
	self.assert_(b.author == "Philip K. Dick")
	
	#test 2 books

	sb = sblist[1]
	b = sb.book
	self.assert_(sb.rating == "90")
	self.assert_(b.isbn == "0679736646")
	self.assert_(b.title == "Ubik", b.title)
	self.assert_(b.author == "Philip K. Dick")
		
	
    def testImportStudentPaper(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	splist = student.studentpaper_set.fetch(9857437)
	
	#test 1 Paper	
	sp = splist[0]
	p = sp.paper
	self.assert_(sp.rating == "67")
	self.assert_(sp.comment == "2009. Gives a detailed overview of cognitive architectures.")
	self.assert_(p.paper_category == "conference")
	self.assert_(p.title == "Cognitive Architectures: Research Issues and Challenges")
	self.assert_(p.author == "Pat Langley, John E. Laird, and Seth Rogers")
	
	sp = splist[1]
	p = sp.paper
	self.assert_(sp.rating == "92")
	self.assert_(sp.comment == "Interesting talk about his experience designing languages")
	self.assert_(p.paper_category == "journal")
	self.assert_(p.title == "The 1980 ACM Turing Award Lecture")
	self.assert_(p.author == "C.A.R. (Tony) Hoare")

	sp = splist[2]
	p = sp.paper
	self.assert_(sp.rating == "90")
	self.assert_(sp.comment == "ACM 1993")
	self.assert_(p.paper_category == "journal")
	self.assert_(p.title == "The Evolution of Lisp")
	self.assert_(p.author == "Guy L. Steele, Jr. and Richard P. Gabriel")

    
    def testImportStudentPaper2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[2]	
	splist = student.studentpaper_set.fetch(9857437)
	
	#test 1 Paper	
	sp = splist[0]
	p = sp.paper
	self.assert_(sp.rating == "83")
	self.assert_(sp.comment == "")
	self.assert_(p.paper_category == "journal")
	self.assert_(p.title == "The New Product Development Game")
	self.assert_(p.author == "Hirotaka Takeuchi and Ikujiro Nanaka")

    def testImportStudentInternship(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	silist = student.studentinternship_set.fetch(9857437)
	
	#test 1 Internship	
	si = silist[0]
	i = si.internship
	self.assert_(si.rating == "5")
	self.assert_(si.comment == "asdklfj")
	self.assert_(i.place_name == "Microsoft")
	self.assert_(i.location == "Seattle")
	self.assert_(i.semester == "Summer 2009")

	#test 2 Internships
	si = silist[1]
	i = si.internship
	self.assert_(si.rating == "25")
	self.assert_(si.comment == "It Sucked!")
	self.assert_(i.place_name == "Valero")
	self.assert_(i.location == "San Antonio")
	self.assert_(i.semester == "Summer 2010")

	#test 3 Internships
	si = silist[2]
	i = si.internship
	self.assert_(si.rating == "4")
	self.assert_(si.comment == "Not my major")	
	self.assert_(i.place_name == "Deloitte")
	self.assert_(i.location == "Houston")
	self.assert_(i.semester == "Summer 2008")


    def testImportStudentInternship2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	silist = student.studentinternship_set.fetch(9857437)
	
	#test 1 Internship	
	si = silist[0]
	i = si.internship
	self.assert_(si.rating == "25")
	self.assert_(si.comment == "Beautiful City")	
	self.assert_(i.place_name == "Facebook")
	self.assert_(i.location == "Mountain View")
	self.assert_(i.semester == "Summer 2008")

	#test 2 Internships	
	si = silist[1]
	i = si.internship
	self.assert_(si.rating == "89")
	self.assert_(si.comment == "It was good")
	self.assert_(i.place_name == "uFollowit")
	self.assert_(i.location == "Austin")
	self.assert_(i.semester == "Summer 2009")

	#test 3 Internships
	si = silist[2]
	i = si.internship
	self.assert_(si.rating == "68")
	self.assert_(si.comment == "Too cold in Wisconsin")	
	self.assert_(i.place_name == "Epic")
	self.assert_(i.location == "Madison")
	self.assert_(i.semester == "Summer 2010")


    def testImportStudentStudyPlace(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	ssplist5 = student.studentplace_set
	
	
	ssplist = []
	for pA in ssplist5:
		if pA.place.place_type == "study_place":
			ssplist.append(pA)	
	
	#test 1 Study Place	
	ssp = ssplist[0]
	sp = ssp.place
	self.assert_(ssp.rating == "4")
	self.assert_(ssp.comment == "A lot of stairs to walk up")
	self.assert_(sp.place_name == "Painter")
	self.assert_(sp.semester == "Fall 2010")

	#test 2 Study Places	
	ssp = ssplist[1]
	sp = ssp.place
	self.assert_(ssp.rating == "45")
	self.assert_(ssp.comment == "It's good when it's not too crowded")
	self.assert_(sp.place_name == "Architecture Library")
	self.assert_(sp.semester == "Fall 2010")

	#test 3 Study Places	
	ssp = ssplist[2]
	sp = ssp.place
	self.assert_(ssp.rating == "3")
	self.assert_(ssp.comment == "Bleh")
	self.assert_(sp.place_name == "PCL")
	self.assert_(sp.semester == "Fall 2010")

  
    def testImportStudentStudyPlace2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	ssplist5 = student.studentplace_set
	
	
	ssplist = []
	for pA in ssplist5:
		if pA.place.place_type == "study_place":
			ssplist.append(pA)
	
	#test 1 Study Place	
	ssp = ssplist[0]
	sp = ssp.place
	self.assert_(ssp.rating == "4")
	self.assert_(ssp.comment == "No cell phone reception")
	self.assert_(sp.place_name == "ENS")
	self.assert_(sp.semester == "Spring 2010")

	#test 2 Study Places	
	ssp = ssplist[1]
	sp = ssp.place
	self.assert_(ssp.rating == "75")
	self.assert_(ssp.comment == "A good place to sleep")
	self.assert_(sp.place_name == "FAC")
	self.assert_(sp.semester == "Fall 2008")

	#test 3 Study Places	
	ssp = ssplist[2]
	sp = ssp.place
	self.assert_(ssp.rating == "85")
	self.assert_(ssp.comment == "Very quiet since no one knows about it.")
	self.assert_(sp.place_name == "Rec Center")
	self.assert_(sp.semester == "Spring 2009")


    def testImportStudentLivePlace(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	slplist5 = student.studentplace_set
	
	
	slplist = []
	for pA in slplist5:
		if pA.place.place_type == "live_place":
			slplist.append(pA)
	
	#test 1 Live Place	
	slp = slplist[0]
	lp = slp.place
	self.assert_(slp.rating == "20")
	self.assert_(slp.comment == "Twas OK")
	self.assert_(lp.place_name == "The Block")
	self.assert_(lp.semester == "Fall 2009")

	#test 2 Live Places
	slp = slplist[1]
	lp = slp.place
	self.assert_(slp.rating == "45")
	self.assert_(slp.comment == "Peace and quiet")
	self.assert_(lp.place_name == "Enfield Townhomes")
	self.assert_(lp.semester == "Spring 2008")

	#test 3 Live Places
	slp = slplist[2]
	lp = slp.place
	self.assert_(slp.rating == "45")
	self.assert_(slp.comment == "Awesome Pool")
	self.assert_(lp.place_name == "Jefferson 26")
	self.assert_(lp.semester == "Spring 2009")


    def testImportStudentLivePlace2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	slplist5 = student.studentplace_set
	
	
	slplist = []
	for pA in slplist5:
		if pA.place.place_type == "live_place":
			slplist.append(pA)
	
	#test 1 Live Place	
	slp = slplist[0]
	lp = slp.place
	self.assert_(slp.rating == "20")
	self.assert_(slp.comment == "I had no car")
	self.assert_(lp.place_name == "University Village")
	self.assert_(lp.semester == "Fall 2007")

	#test 2 Live Places	
	slp = slplist[1]
	lp = slp.place
	self.assert_(slp.rating == "85")
	self.assert_(slp.comment == "Peace and quiet")
	self.assert_(lp.place_name == "Blackstone Apts")
	self.assert_(lp.semester == "Spring 2010")

	#test 3 Live Places	
	slp = slplist[2]
	lp = slp.place
	self.assert_(slp.rating == "90")
	self.assert_(slp.comment == "On Riverside")
	self.assert_(lp.place_name == "Landry Place Apts")
	self.assert_(lp.location == "2239 Cromwell Cir.")

    
    def testImportStudentEatPlace(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	seplist5 = student.studentplace_set
	
	
	seplist = []
	for pA in seplist5:
		if pA.place.place_type == "eat_place":
			seplist.append(pA)
	
	#test 1 Eat Place	
	sep = seplist[0]
	ep = sep.place
	self.assert_(sep.rating == "45")
	self.assert_(sep.comment == "WINGS")
	self.assert_(ep.place_name == "Pluckers")
	self.assert_(ep.semester == "Spring 2009")

	#test 2 Eat Places	
	sep = seplist[1]
	ep = sep.place
	self.assert_(sep.rating == "45")
	self.assert_(sep.comment == "Drunken Food")
	self.assert_(ep.place_name == "What-A-Burger")
	self.assert_(ep.semester == "Spring 2010")

	#test 3 Eat Places	
	sep = seplist[2]
	ep = sep.place
	self.assert_(sep.rating == "45")
	self.assert_(sep.comment == "3 AM Drunkfest")
	self.assert_(ep.place_name == "Taco C")
	self.assert_(ep.semester == "Fall 2007")


    def testImportStudentEatPlace2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	seplist5 = student.studentplace_set
	
	
	seplist = []
	for pA in seplist5:
		if pA.place.place_type == "eat_place":
			seplist.append(pA)	
	#test 1 Eat Place	
	sep = seplist[0]
	ep = sep.place
	self.assert_(sep.rating == "95")
	self.assert_(sep.comment == "Free Dessert")
	self.assert_(ep.place_name == "Carinos")
	self.assert_(ep.location == "Brodie Lane")

	#test 2 Eat Places	
	sep = seplist[1]
	ep = sep.place
	self.assert_(sep.rating == "83")
	self.assert_(sep.comment == "Thai Food")
	self.assert_(ep.place_name == "Madam Mam's")
	self.assert_(ep.location == "Guadalupe")

	#test 3 Eat Places	
	sep = seplist[2]
	ep = sep.place
	self.assert_(sep.rating == "87")
	self.assert_(sep.comment == "3 AM Drunkfest")
	self.assert_(ep.place_name == "Kerbey Lane")
	self.assert_(ep.semester == "Fall 2006")

   
     
    def testImportStudentFunPlace(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	sfplist5 = student.studentplace_set
	
	
	sfplist = []
	for pA in sfplist5:
		if pA.place.place_type == "fun_place":
			sfplist.append(pA)
	
	#test 1 Fun Place	
	sfp = sfplist[0]
	fp = sfp.place
	self.assert_(sfp.rating == "45")
	self.assert_(sfp.comment == "Eat and Play combo")
	self.assert_(fp.place_name == "Dave and Busters")
	self.assert_(fp.semester == "Spring 2009")

	#test 2 Fun Places	
	sfp = sfplist[1]
	fp = sfp.place
	self.assert_(sfp.rating == "45")
	self.assert_(sfp.comment == "Glow in the dark golf")
	self.assert_(fp.place_name == "Main Event")
	self.assert_(fp.location == "Anderson Mill")

	#test 3 Fun Places	
	sfp = sfplist[2]
	fp = sfp.place
	self.assert_(sfp.rating == "45")
	self.assert_(sfp.comment == "All the bars in one street")
	self.assert_(fp.place_name == "Downtown")
	self.assert_(fp.semester == "Spring 2010")


    def testImportStudentFunPlace2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	sfplist5 = student.studentplace_set
	
	sfplist = []
	for pA in sfplist5:
		if pA.place.place_type == "fun_place":
			sfplist.append(pA)
	
	#test 1 Fun Place	
	sfp = sfplist[0]
	fp = sfp.place
	self.assert_(sfp.rating == "99")
	self.assert_(sfp.comment == "Events everywhere")
	self.assert_(fp.place_name == "Las Vegas")
	self.assert_(fp.location == "Nevada")

	#test 2 Fun Places	
	sfp = sfplist[1]
	fp = sfp.place
	self.assert_(sfp.rating == "80")
	self.assert_(sfp.comment == "Bowling")
	self.assert_(fp.place_name == "Union Underground")
	self.assert_(fp.location == "Student Union")

	#test 3 Fun Places	
	sfp = sfplist[2]
	fp = sfp.place
	self.assert_(sfp.rating == "97")
	self.assert_(sfp.comment == "Great Music")
	self.assert_(fp.place_name == "ACL")
	self.assert_(fp.semester == "Fall 2010")


    def testImportStudentGame(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[0]	
	sglist = student.studentgame_set.fetch(9857437)
	
	#test 1 Game	
	sg = sglist[0]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "dsaf")
	self.assert_(g.os == "Any")
	self.assert_(g.title == "Zork II")

	#test 2 Games	
	sg = sglist[1]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "The players look so real")
	self.assert_(g.os == "Any")
	self.assert_(g.title == "FIFA 2011")

	#test 3 Game	
	sg = sglist[2]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "It's a crime to be this good")
	self.assert_(g.os == "Any")
	self.assert_(g.title == "Call of Duty: Modern Warfare")


    def testImportStudentGame2(self) :

        self.dbClear()
	xmlImportFile('xml/ASN1.xml')
	query = Student.all()
	students = query.fetch(5)
	student = students[3]	
	sglist = student.studentgame_set.fetch(9857437)
	
	#test 1 Game	
	sg = sglist[0]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "Steal cars and make money")
	self.assert_(g.os == "Any")
	self.assert_(g.title == "Grand Theft Auto")

	#test 2 Games	
	sg = sglist[1]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "Too many mouse clicks")
	self.assert_(g.title == "World of War Craft")
	self.assert_(g.os == "Any")

	#test 3 Game
	sg = sglist[2]
	g = sg.game
	self.assert_(sg.rating == "5")
	self.assert_(sg.comment == "AMAZING!!")
	self.assert_(g.os == "Any")
	self.assert_(g.title == "Super Smash Brothers")



