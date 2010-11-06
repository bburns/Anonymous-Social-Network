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

     def testValidationCourseNum(self) :
	self.assertRaises(db.BadValueError, validate_course_num, "AI")
 	self.assertRaises(db.BadValueError, validate_course_num, "12345")




