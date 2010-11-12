#!/usr/bin/env python

# -------------------------------
# testValidation.py
# Copyright (C) 2010
# Sang Yun
# -------------------------------

# -------
# imports
# -------

import unittest
from google.appengine.ext import db
from models import *
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

# -----------
# TestValidation
# -----------

class testValidation (unittest.TestCase) :

    # Course Num

    def testValidationCourseNum(self) :
        self.assertRaises(db.BadValueError, validate_course_num, "CS")
        self.assertRaises(db.BadValueError, validate_course_num, "373")
        self.assertRaises(db.BadValueError, validate_course_num, "      ")
        self.assertRaises(db.BadValueError, validate_course_num, " ")

        self.assert_(validate_course_num("CS 373") is None)
        self.assert_(validate_course_num("ABC 123") is None)


    # Unique number
    def testValidationUnique(self) :
        # input is non-integer value
        self.assertRaises(db.BadValueError, validate_unique, "asdfg")
        self.assertRaises(db.BadValueError, validate_unique, "unique")
        self.assertRaises(db.BadValueError, validate_unique, "asdfg2000")
        self.assertRaises(db.BadValueError, validate_unique, "unique123345")

        # input is integer but with invalid length
        self.assertRaises(db.BadValueError, validate_unique, "1")
        self.assertRaises(db.BadValueError, validate_unique, "123")
        self.assertRaises(db.BadValueError, validate_unique, "1234")
        self.assertRaises(db.BadValueError, validate_unique, "1234567890")
        self.assertRaises(db.BadValueError, validate_unique, "12345126936")

        self.assert_(validate_unique("12345") is None)


    # Semester    
    def testValidationSemester(self) :
        # input is does not have year
        self.assertRaises(db.BadValueError, validate_semester, "Fall")
        self.assertRaises(db.BadValueError, validate_semester, "Spring")
        
        # input is does not have semester
        self.assertRaises(db.BadValueError, validate_semester, "2010")
        self.assertRaises(db.BadValueError, validate_semester, "1999")

        # input semester is not Fall or Spring
        self.assertRaises(db.BadValueError, validate_semester, "Foo 2010")
        self.assertRaises(db.BadValueError, validate_semester, "Bar 1999")

        # input does not have valid year
        self.assertRaises(db.BadValueError, validate_semester, "Fall 1")
        self.assertRaises(db.BadValueError, validate_semester, "Spring 23")

        # input is random strings
        self.assertRaises(db.BadValueError, validate_semester, "asdfasdf")
        self.assertRaises(db.BadValueError, validate_semester, "Asdf 3001")

        self.assert_(validate_semester("Spring 2010") is None)
        self.assert_(validate_semester("Summer 2000") is None)
        self.assert_(validate_semester("Fall 2012") is None)


    # Rating
    def testValidationRating(self) :
        self.assertRaises(db.BadValueError, validate_rating, "asdf")
        self.assertRaises(db.BadValueError, validate_rating, "Foo")
        self.assertRaises(db.BadValueError, validate_rating, "   ")
        self.assertRaises(db.BadValueError, validate_rating, "...")
        self.assertRaises(db.BadValueError, validate_rating, "-10")
        self.assertRaises(db.BadValueError, validate_rating, "-200")
        self.assertRaises(db.BadValueError, validate_rating, "101")
        self.assertRaises(db.BadValueError, validate_rating, "200")

        self.assert_(validate_rating("0") is None)
        self.assert_(validate_rating("100") is None)
        self.assert_(validate_rating("75") is None)


    # Email
    def testValidationEmail(self) :
        # Email is does not have @ or dot com
        self.assertRaises(db.BadValueError, validate_email, "asdf")
        self.assertRaises(db.BadValueError, validate_email, "asdf1234@asdf")
        self.assertRaises(db.BadValueError, validate_email, "asdf#asdf.com")
        
        # Email has more than two dots or have numbers in domain
        self.assertRaises(db.BadValueError, validate_email, "asdf@123.a.s.d.f.c")
        self.assertRaises(db.BadValueError, validate_email, "asdf1234@1234.com")


    # ISBN
    def testValidationIsbn(self):
        self.assertRaises(db.BadValueError, validate_isbn, "  ")
        self.assertRaises(db.BadValueError, validate_isbn, "123")
        self.assertRaises(db.BadValueError, validate_isbn, "12345678901") # too long
        self.assertRaises(db.BadValueError, validate_isbn, "12345678901234") # too long
        self.assertRaises(db.BadValueError, validate_isbn, "abc")
        self.assertRaises(db.BadValueError, validate_isbn, "abcdefghij") # 10 chars

        self.assert_(validate_isbn("") is None) # empty is okay
        self.assert_(validate_isbn("1234567890") is None) # 10 digits
        self.assert_(validate_isbn("1234567890123") is None) # 13 digits
        
        
    # Grade
    def testGrade(self):
        self.assertRaises(db.BadValueError, validate_grade, "2")
        self.assertRaises(db.BadValueError, validate_grade, "3.5")
        self.assertRaises(db.BadValueError, validate_grade, "K")
        self.assertRaises(db.BadValueError, validate_grade, "A+")
        
        self.assert_(validate_grade("A") is None)
        self.assert_(validate_grade("A-") is None)
