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

     # input is just alphabets or just numbers
     def testValidationCourseNum(self) :
	self.assertRaises(db.BadValueError, validate_course_num, "CS")
 	self.assertRaises(db.BadValueError, validate_course_num, "373")

     # input is multiple spaces
     def testValidationCourseNum2(self) :
	self.assertRaises(db.BadValueError, validate_course_num, "      ")
 	self.assertRaises(db.BadValueError, validate_course_num, " ")

     # input is non-integer value
     def testValidationUnique(self) :
	self.assertRaises(db.BadValueError, validate_unique, "asdfg")
	self.assertRaises(db.BadValueError, validate_unique, "unique")
	self.assertRaises(db.BadValueError, validate_unique, "asdfg2000")
	self.assertRaises(db.BadValueError, validate_unique, "unique123345")
        # self.assertRaises(db.BadValueError, validate_unique, "12345126936")

     # input is integer but with invalid length
     def testValidationUnique2(self) :
	self.assertRaises(db.BadValueError, validate_unique, "1")
	self.assertRaises(db.BadValueError, validate_unique, "123")
	self.assertRaises(db.BadValueError, validate_unique, "1234")
	#self.assertRaises(db.BadValueError, validate_unique, "1234567890")


     # input is does not have year
     def testValidationSemester(self) :
	self.assertRaises(db.BadValueError, validate_semester, "Fall")
        self.assertRaises(db.BadValueError, validate_semester, "Spring")

     # input is does not have semester
     def testValidationSemester2(self) :
	self.assertRaises(db.BadValueError, validate_semester, "2010")
        self.assertRaises(db.BadValueError, validate_semester, "1999")

     # input semester is not Fall or Spring
     def testValidationSemester3(self) :
	self.assertRaises(db.BadValueError, validate_semester, "Foo 2010")
        self.assertRaises(db.BadValueError, validate_semester, "Bar 1999")

     # input does not have valid year
     def testValidationSemester4(self) :
	self.assertRaises(db.BadValueError, validate_semester, "Fall 1")
        self.assertRaises(db.BadValueError, validate_semester, "Spring 23")

    # input is random strings
     def testValidationSemester5(self) :
	self.assertRaises(db.BadValueError, validate_semester, "asdfasdf")
        self.assertRaises(db.BadValueError, validate_semester, "Asdf 3001")

     # Rating input is non-integer
     def testValidationRating(self) :
	self.assertRaises(db.BadValueError, validate_semester, "asdf")
        self.assertRaises(db.BadValueError, validate_semester, "Foo")

     # Rating input is space charcters or symbols
     def testValidationRating2(self) :
	self.assertRaises(db.BadValueError, validate_semester, "   ")
        self.assertRaises(db.BadValueError, validate_semester, "...")

     # Rating input is negative
     def testValidationRating3(self) :
	self.assertRaises(db.BadValueError, validate_semester, "-10")
        self.assertRaises(db.BadValueError, validate_semester, "-200")

     # Rating input is non-integer
     def testValidationRating4(self) :
	self.assertRaises(db.BadValueError, validate_semester, "101")
        self.assertRaises(db.BadValueError, validate_semester, "200")

     # Email is does not have @ or dot com
     def testValidationEmail(self) :
	self.assertRaises(db.BadValueError, validate_email, "asdf")
	self.assertRaises(db.BadValueError, validate_email, "asdf1234@asdf")
	self.assertRaises(db.BadValueError, validate_email, "asdf#asdf.com")

     # Email has more than two dots or have numbers in domain
     def testValidationEmail2(self) :
	self.assertRaises(db.BadValueError, validate_email, "asdf@123.a.s.d.f.c")
	self.assertRaises(db.BadValueError, validate_email, "asdf1234@1234.com")

