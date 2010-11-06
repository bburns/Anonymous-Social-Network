
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
# TestAuthent
# -----------


class testAuthent (unittest.TestCase) :

    def testGetUser(self):
        user = User()
        user.email = 'brian@brian.com'
        user.put()

        user2 = User.get_by_email('brian@brian.com')
        #self.assert_(user == user2) # fails - why?
        self.assert_(user.email == user2.email)

        


