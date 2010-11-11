#!/usr/bin/env python

# -------------------------------
# TestExport.py
# Copyright (C) 2010
# Jonathan Grimes
# -------------------------------

# -------
# imports
# -------

import unittest
import StringIO
from google.appengine.ext import db
from models import *
from utils.xmlExport import *


# -------------
# testExport
# -------------

class testExport (unittest.TestCase) :

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



    def testExport(self):
        self.dbClear()
        s1 = Student()
        s1.id_ = "brian"
        s1.put()
        s2 = Student()
        s2.put()
        students = [s1, s2]
        output = xmlExport(students)
        expected = u'<?xml version="1.0" ?><students><student><id>brian</id></student><student/></students>'
        self.assert_(output == expected, output)


    def testExportEmpty(self):
        self.dbClear()
        students = []
        output = xmlExport(students)
        expected = u'<?xml version="1.0" ?><students/>'
        self.assert_(output == expected, output)


    def testExportClasses(self):
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        c1 = Class()
        c1.course_num = "CS 373"
        c1.put()
        sc = StudentClass()
        sc.student = s1
        sc.class_ = c1
        sc.unique = "12345"
        sc.rating = "85"
        sc.comment = "okay"
        sc.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><class><unique>12345</unique><course_num>CS 373</course_num><rating>85</rating><comment>okay</comment></class></student><student/></students>'
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportBooks(self):
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        b1 = Book()
        b1.title = "Catcher in the Rye"
        b1.put()
        sb = StudentBook()
        sb.student = s1
        sb.book = b1
        sb.rating = "90"
        sb.comment = "woo"
        sb.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><book><title>Catcher in the Rye</title><rating>90</rating><comment>woo</comment></book></student><student/></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportPapers(self) :
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        p1 = Paper()
        p1.title = "The Joy of Pair Programming"
        p1.paper_category = "journal"
        p1.put()
        sp = StudentPaper()
        sp.student = s1
        sp.paper = p1
        sp.rating = "91"
        sp.comment = "duhr"
        sp.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><paper><paper_category>journal</paper_category><title>The Joy of Pair Programming</title><rating>91</rating><comment>duhr</comment></paper></student><student/></students>'
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportInternships(self) :
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        i1 = Internship()
        i1.place_name = "Houston, TX"
        i1.put()
        si = StudentInternship()
        si.student = s1
        si.internship = i1
        si.rating = "99"
        si.comment = ""  # empty comment - should skip the element
        si.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><internship><place_name>Houston, TX</place_name><rating>99</rating></internship></student><student/></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)

        
    def testExportGames(self) :
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        g1 = Game()
        g1.title = "Starcraft 2"
        g1.put()
        sg = StudentGame()
        sg.student = s1
        sg.game = g1
        sg.rating = "5"
        sg.comment = "ummmm"
        sg.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><game><title>Starcraft 2</title><rating>5</rating><comment>ummmm</comment></game></student><student/></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportStudyPlace(self) :
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan"
        s1.put()
        s2 = Student()
        s2.put()
        p1 = Place()
        p1.place_type = "study_place"
        p1.place_name = "archlib"
        p1.location = "campus"
        p1.semester = "Fall 2010"
        p1.put()
        sp = StudentPlace()
        sp.student = s1
        sp.place = p1
        sp.rating = "95"
        sp.comment = "it's nice"
        sp.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan</id><study_place><place_name>archlib</place_name><location>campus</location><semester>Fall 2010</semester><rating>95</rating><comment>it\'s nice</comment></study_place></student><student/></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportFunPlace(self) :
        "Try two students both referencing the same place object"
        self.dbClear()
        s1 = Student()
        s1.id_ = "jon"
        s1.put()
        s2 = Student()
        s2.id_ = "brian"
        s2.put()
        p1 = Place()
        p1.place_type = "fun_place"
        p1.place_name = "bob wentz park"
        p1.location = "lake travis"
        p1.semester = "Fall 2010"
        p1.put()
        sp = StudentPlace()
        sp.student = s1
        sp.place = p1
        sp.rating = "90"
        sp.put()
        sp = StudentPlace()
        sp.student = s2
        sp.place = p1
        sp.rating = "95"  # a different rating for the same place
        sp.comment = "fun"
        sp.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>jon</id><fun_place><place_name>bob wentz park</place_name><location>lake travis</location><semester>Fall 2010</semester><rating>90</rating></fun_place></student><student><id>brian</id><fun_place><place_name>bob wentz park</place_name><location>lake travis</location><semester>Fall 2010</semester><rating>95</rating><comment>fun</comment></fun_place></student></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportEatPlace(self) :
        "one student with two places"
        self.dbClear()
        s1 = Student()
        s1.id_ = "jon"
        s1.put()
        p1 = Place()
        p1.place_type = "eat_place"
        p1.place_name = "dirty martin's"
        p1.location = "guadalupe"
        p1.semester = "Fall 2010"
        p1.put()
        p2 = Place()
        p2.place_type = "eat_place"
        p2.place_name = "india's"
        p2.location = "houston"
        p2.semester = "Fall 2010"
        p2.put()
        sp = StudentPlace()
        sp.student = s1
        sp.place = p1
        sp.rating = "93"
        sp.put()
        sp = StudentPlace()
        sp.student = s1
        sp.place = p2
        sp.rating = "94"
        sp.put()
        students = [s1]
        expected = u'<?xml version="1.0" ?><students><student><id>jon</id><eat_place><place_name>dirty martin\'s</place_name><location>guadalupe</location><semester>Fall 2010</semester><rating>93</rating></eat_place><eat_place><place_name>india\'s</place_name><location>houston</location><semester>Fall 2010</semester><rating>94</rating></eat_place></student></students>' 
        output = xmlExport(students)
        self.assert_(output == expected, output)


    def testExportMultipleObjects(self) :
        self.dbClear()
        s1 = Student()
        s1.id_ = "Jonathan Grimes"
        s1.password = "password"
        s1.put()
        s2 = Student()
        s2.id_ = "Brian Burns"
        s2.password = "password"
        s2.put()
        c1 = Class()
        c1.course_num = "CS 373"
        c1.put()
        c2 = Class()
        c2.course_num = "CS 343"
        c2.put()
        sc = StudentClass()
        sc.student = s1
        sc.class_ = c1
        sc.unique = "12345"
        sc.rating = "90"
        sc.put()
        sc = StudentClass()
        sc.student = s1
        sc.class_ = c2
        sc.unique = "45678"
        sc.comment = "foo"
        sc.rating = "80"
        sc.put()
        students = [s1,s2]
        expected = u'<?xml version="1.0" ?><students><student><id>Jonathan Grimes</id><password>password</password><class><unique>12345</unique><course_num>CS 373</course_num><rating>90</rating></class><class><unique>45678</unique><course_num>CS 343</course_num><rating>80</rating><comment>foo</comment></class></student><student><id>Brian Burns</id><password>password</password></student></students>'
        output = xmlExport(students)
        self.assert_(output == expected, output)

