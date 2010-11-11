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



    
    # this works, though adds about 4 secs to unit test runtime, so commenting it out
    # def testImportExport(self):
    #     """
    #     Pseudo-acceptance test - import-export-import cycle. 
    #     Import all our xml data, export it to a string, 
    #     then clear the database, import that string, export the database, 
    #     and compare the strings - they should match. 
    #     """

    #     self.dbClear()

    #     # import all our data
    #     xmlImportFile("xml/ASN1.xml")
        
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

