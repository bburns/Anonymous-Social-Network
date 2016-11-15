import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *



# Link

class DeleteLink(webapp.RequestHandler):
    def get(self):
        typename = self.request.get('typename') # eg 'StudentBook'
        link_id = int(self.request.get('link_id')) 
        cl = globals()[typename]
        link = cl.get_by_id(link_id)
        doRender(self,'link/delete.html',{'link':link, 'typename':typename, 'link_id':link_id})

    def post(self):
        typename = self.request.get('typename')
        link_id = int(self.request.get('link_id')) 
        cl = globals()[typename]
        link = cl.get_by_id(link_id)
        link.delete() # will update average rating, etc
        self.redirect("/profile")
