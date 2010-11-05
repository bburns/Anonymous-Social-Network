
#!/usr/bin/env python

# -------------------------------
# TestASN1.py
# Copyright (C) 2010
# Jonathan Grimes
# -------------------------------

# -------
# imports
# -------

import unittest
from google.appengine.ext import db
from models import *



# -----------
# TestASN1
# -----------


class testAuthent (unittest.TestCase) :

    # def dbClear(self):
    #     "A helper method to clear the database"
    #     #. do for all tables? 
    #     query = Student.all()
    #     db.delete(query)


    def testGetUser(self):
        user = User()
        user.email = 'brian@google.com'
        user.put()

        user2 = User.get_by_email('brian@google.com')
        #self.assert_(user == user2) # fails - why?
        self.assert_(user.email == user2.email)




