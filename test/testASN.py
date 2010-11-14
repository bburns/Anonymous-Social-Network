#!/usr/bin/env python

# -------------------------------
# TestASN.py
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
from utils.xmlExport import *



# -----------
# TestASN
# -----------


class testASN (unittest.TestCase) :

    def dbClear(self):
        "A helper method to clear the database"

        # you actually have to clear the association tables also -
        # even if you delete all the related objects, the association objects
        # are still there!
        # which makes sense, as appengine doesn't know they're just association objects.
        tables = [Student, Class, Book, Paper, Internship, Place, Game]
        tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
        for table in tables:
            query = table.all()
            db.delete(query)



    
    # this works, though adds about 4 secs to unit test runtime, so leave it commented out

    # def testImportExport(self):
    #     """
    #     Pseudo-acceptance test - import-export-import cycle. 
    #     Import all our xml data, export it to a string, 
    #     then clear the database, import that string, export the database, 
    #     and compare the strings - they should match. 
    #     """

    #     self.dbClear()

    #     # import all our data
    #     xmlImportFile("../xml/ASN.xml")
        
    #     # export it
    #     students = Student.all()
    #     xml = xmlExport(students)

    #     # clear the database and import that xml string
    #     self.dbClear()
    #     xmlImportString(xml)

    #     # now export the database and compare the two strings - should match
    #     students = Student.all()
    #     xml2 = xmlExport(students)
    #     self.assert_(xml == xml2, 'xml: ' + xml + '\nxml2: ' + xml2)


    def testStudent(self) :

        self.dbClear()
        s = Student()
        s.id_ = "TestStudent"
        s.password = "12345"
        s.put()
        query = Student.all()
        assert len(query.fetch(10)) == 1
        student = query.filter("id_ = ", "TestStudent").fetch(5)
        #results = query.fetch(10)
        #for student in results:
        #print student.id_
        #print student.password
        assert student[0].id_ == "TestStudent"
        self.assert_(student[0].password == "12345")


    def testStudentBook(self) :

        self.dbClear()
        s = Student()
        s.id_ = "TestStudent"
        s.password = "12345"
        s.put()

        b = Book()
        b.title = "Valis"
        b.isbn = "0679734465"
        b.author = "Philip K. Dick"
        b.put()

        sb = StudentBook()
        sb.student = s
        sb.book = b
        sb.rating = "5"
        sb.comment = "crazy"
        sb.put()

        b = Book()
        b.title = "Ubik"
        b.isbn = "0679736646"
        b.author = "Philip K. Dick"
        b.put()

        sb = StudentBook()
        sb.student = s
        sb.book = b
        sb.rating = "4"
        sb.comment = "don't remember"
        sb.put()

        # for sb in s.studentbook_set:
        #     book = sb.book.title
        #     print book

        titles = [sb.book.title for sb in s.studentbook_set]
        self.assert_(titles == ['Valis','Ubik'])





    def testFindAddClass(self):
        
        self.dbClear()

        c = Class()
        c.course_num = "CS 373"
        c.course_name = "Software Engineering"
        c.instructor = "Downing"
        c.put()

        # find or add an existing class - 
        # ignores course name, fuzzy match on instructor
        c = Class.findAdd("CS 373", "swe", "Downing")
        self.assert_(c.course_name == "Software Engineering")

        # fuzzy match on instructor (longer name)
        c = Class.findAdd("CS 373", "swe", "Glen Downing")
        self.assert_(c.course_name == "Software Engineering")


        # add a new class
        c = Class.findAdd("CS 343", "AI", "Ray Mooney")
        self.assert_(c.instructor == "Ray Mooney")

        # fuzzy match on instructor (shorter name)
        c = Class.findAdd("CS 343", "A.I.", "Mooney")
        self.assert_(c.instructor == "Ray Mooney")



    def testFindAddBook(self):
        
        self.dbClear()

        b = Book()
        b.title = "Valis"
        b.isbn = "0679734465"
        b.author = "Philip K. Dick"
        b.put()

        # find or add an existing book
        b = Book.findAdd("Valis")
        self.assert_(b.isbn == "0679734465")

        # add a new book
        b = Book.findAdd("Ubik", "pkdick", "1234567890")
        self.assert_(b.isbn == "1234567890")



    def testFindAddPaper(self):
        
        self.dbClear()

        o = Paper()
        o.paper_category = "journal"
        o.title = "Lambda the Ultimate"
        o.author = "Anonymous"
        o.put()

        # find or add an existing paper
        o = Paper.findAdd("Lambda the Ultimate")
        self.assert_(o.author == "Anonymous")

        # add a new paper
        o = Paper.findAdd("Lambda something", "Lance Armstrong", "journal")
        self.assert_(o.author == "Lance Armstrong")



    def testFindAddInternship(self):
        
        self.dbClear()

        o = Internship()
        o.place_name = "Google"
        o.location = "California"
        o.semester = "Summer 2009"
        o.put()

        # find or add an existing item
        o = Internship.findAdd("Google")
        self.assert_(o.location == "California")

        # add a new item
        o = Internship.findAdd("Microsoft", "Seattle", "Fall 2004")
        self.assert_(o.location == "Seattle")



    def testFindAddPlace(self):
        
        self.dbClear()

        o = Place()
        o.place_type = "eat_place"
        o.place_name = "Los Tios"
        o.location = "Houston"
        o.semester = "Summer 2000"
        o.put()

        # find or add an existing item
        o = Place.findAdd("eat_place", "Los Tios")
        self.assert_(o.location == "Houston")

        # add a new item
        o = Place.findAdd("eat_place", "Taco Cabana", "Austin", "Summer 1999")
        self.assert_(o.location == "Austin")


    def testFindAddGame(self):
        
        self.dbClear()

        o = Game()
        o.title = "Zork"
        o.os = "Any"
        o.put()

        # find or add an existing item
        o = Game.findAdd("Zork")
        self.assert_(o.os == "Any")

        # find or add an existing item
        o = Game.findAdd("Zork", "Apple II")
        self.assert_(o.os == "Any") # will ignore os in search

        # add a new item
        o = Game.findAdd("Ultima I", "Apple II")
        self.assert_(o.os == "Apple II")



    # Grades

    def testGradeToNum(self):
        
        self.assert_(Grade.gradeToNum('A')==4.0)
        self.assert_(Grade.gradeToNum('A-')==3.7)
        self.assert_(Grade.gradeToNum('B+')==3.3)
        self.assert_(Grade.gradeToNum('B')==3.0)
        self.assert_(Grade.gradeToNum('B-')==2.7)
        self.assert_(Grade.gradeToNum('F')==0.0)


    def testNumToGrade(self):
        
        self.assert_(Grade.numToGrade(0)=='F')
        self.assert_(Grade.numToGrade(4)=='A')
        self.assert_(Grade.numToGrade(3.7)=='A-')
        self.assert_(Grade.numToGrade(3.8)=='A-')
        self.assert_(Grade.numToGrade(3.9)=='A')
        self.assert_(Grade.numToGrade(1.0)=='D')
        self.assert_(Grade.numToGrade(1.3)=='D+')
        self.assert_(Grade.numToGrade(1.4)=='D+')



    def testAvgGrades(self):

        self.assert_(Grade.getAvgGrade(['A','C']) == 'B')
        self.assert_(Grade.getAvgGrade(['A','','','']) == 'A')
        self.assert_(Grade.getAvgGrade(['A','A','A-']) == 'A')
        self.assert_(Grade.getAvgGrade(['A','A','A','B']) == 'A-') # 4*3+3=15/4=3.75
        self.assert_(Grade.getAvgGrade(['A','A','A','B+']) == 'A-') # 4*3+3.3=15.3/4=3.825
        self.assert_(Grade.getAvgGrade(['A','A','A','A','B+']) == 'A-') # 4*4+3.3=19.3/5=3.86
        self.assert_(Grade.getAvgGrade(['A','A','A','A-']) == 'A') # 4*3+3.7=15.7/4=3.925
        
        self.assert_(Grade.getAvgGrade([]) == '')
        self.assert_(Grade.getAvgGrade(['','','']) == '')
        self.assert_(Grade.getAvgGrade(['','Q','CR']) == '')

        self.assert_(Grade.getAvgGrade(['A']) == 'A')
        self.assert_(Grade.getAvgGrade(['A-']) == 'A-')
        self.assert_(Grade.getAvgGrade(['B+']) == 'B+')
        self.assert_(Grade.getAvgGrade(['B']) == 'B')
        self.assert_(Grade.getAvgGrade(['B-']) == 'B-')
        self.assert_(Grade.getAvgGrade(['D-']) == 'D-')
        self.assert_(Grade.getAvgGrade(['F']) == 'F')


    def testAvgGrades2(self):
        
        self.dbClear()

        c = Class()
        c.course_num = "CS 373"
        c.course_name = "Software Engineering"
        c.instructor = "Downing"
        c.put()

        s = Student()
        s.id_ = "test0000"
        s.put()

        link = StudentClass()
        link.student = s
        link.class_ = c
        link.rating = "80"
        link.grade = "C"
        link.put()

        s = Student()
        s.id_ = "test0001"
        s.put()

        link = StudentClass()
        link.student = s
        link.class_ = c
        link.rating = "90"
        link.grade = "A"
        link.put()

        self.assert_(c.gradeAvg == "B")



    """
    def testStudentBook2(self):

        self.dbClear()
        s = Student()
        s.id_ = "TestStudent"
        s.password = "12345"
        s.put()

        # add two new books
        s.addBook("Valis", "pkdick", '', "4", "weird")
        s.addBook("Ubik", "pkdick", '', "4", "can't remember") # can't pass 4 - must be a float

        b = Book()
        b.title = "The Hobbit"
        b.isbn = "12345"
        b.put()

        # add an existing book
        s.addBook("The Hobbit")

        titles = [sb.book.title for sb in s.studentbook_set]
        self.assert_(titles == ['Valis','Ubik','The Hobbit'], titles)
        self.assert_(s.studentbook_set[2].book.isbn == "12345")
    """

