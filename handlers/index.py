
"""
ASN2
Anonymous Social Network phase 2
This file defines all the request handlers for the application.
URL redirections are defined at the end of the file.
"""

import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from utils.xmlExport import xmlExport
from utils.xmlImport import xmlImportString
from utils.sessions import Session
from utils.doRender import doRender
from models import *
#from handlers import *
from handlers.ClassHandler import * 
from handlers.BookHandler import *
from handlers.PaperHandler import *
from handlers.PlaceHandler import *
from handlers.InternshipHandler import *
from handlers.GameHandler import *
from handlers.StudentHandler import *

from google.appengine.ext.db import djangoforms

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self,'index.html')

class Help(webapp.RequestHandler):
    def get(self):
        doRender(self,"help.html")

class About(webapp.RequestHandler):
    def get(self):
        doRender(self,"about.html")


class ChangePassword(webapp.RequestHandler):
    def get(self):
        doRender(self,'changePassword.html',{})

    def post(self):
        values = {}
        self.session = Session()
        oldPass = self.request.get('oldPass')
        newPass1 = self.request.get('newPass1')
        newPass2 = self.request.get('newPass2')
        username = self.session['username']
        user = Student.get_by_username(username)
        
        if oldPass != user.password:
            values['oldPassError'] = True

        if newPass1 != newPass2:
            values['mismatch'] = True

        if oldPass == user.password and newPass1 == newPass2:
            user.password = newPass1
            user.put()
            values['success'] = True
            
        doRender(self,'changePassword.html', values)


class StudentProfile(webapp.RequestHandler):
    def get(self):
        session = Session()
        if 'student_id' in session: 
            template = {}
            sb = StudentBook.all()
            sc = StudentClass.all()
            sp = StudentPlace.all()
            si = StudentInternship.all()
            spa = StudentPaper.all()
            sg = StudentGame.all()
            
            s = Student.get_by_id(session['student_id'])
            
            #books
            sbooks = sb.filter("student =", s)
            sbooks = sbooks.fetch(98988)		
            template['sbooks'] = sbooks

            #class
            sclasses = sc.filter("student =", s)
            sclasses = sclasses.fetch(98988)
            template['sclasses'] = sclasses

            #Place
            splaces = sp.filter("student = ", s)
            splaces = splaces.fetch(98988)
            template['splaces'] = splaces

            #Internship
            sinternships = si.filter("student = ", s)
            sinternships = sinternships.fetch(98988)
            template['sinternships'] = sinternships

            #Paper
            spapers = spa.filter("student = ", s)
            spapers = spapers.fetch(98988)
            template['spapers'] = spapers

            #Game
            sgames = sg.filter("student = ", s)
            sgames = sgames.fetch(98988)
            template['sgames'] = sgames
            
            doRender(self,"profile.html", template)
        else:	 
            doRender(self,"profile.html")


class ListStudent(webapp.RequestHandler):
    def get(self):
        students = Student.all()        
        doRender(self,'student/list.html',{'students':students})



class SignupHandler(webapp.RequestHandler):
    def get(self) :
        self.session = Session()
        self.session.delete_item('username')
        s = Student()
        s.generateID()
        s.generatePassword() 
        s.put()
        user = s
        user.put()
        self.session['username'] = user.id_
        self.session['student_id'] = s.key().id()
        doRender(self, 'issueAccount.html', {'student' : s})

    # old version - let user enter their username (email) and password
    """
    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        doRender(self,'signup.html')
        
    def post(self):
        self.session = Session()
        form = UserForm(self.request.POST)
        if form.is_valid() :
            # check if username already exists
            username = self.request.get('username')
            if Student.get_by_username(username):
                doRender(self,'signup.html',{'error': "Sorry, that username already exists. Please try another one."})
                return
            s = Student()
            #s.generateID()
            s.id_ = username
            s.password = self.request.get('password')
            s.put()
            user = form.save()
            user = s
            user.put()
            self.session['username'] = user.id_
            self.session['student_id'] = s.key().id()
            self.redirect('/')
        else:
            doRender(self,'signup.html', {'error': "Could not process the information please check the following and try again: <br/>- all the fields are filled in. <br/>- valid email address entered."})
      """



class LoginHandler(webapp.RequestHandler):
    def get(self):
        doRender(self,'login.html')

    def post(self):
        self.session = Session()
        id_ = self.request.get('username')        
        pw = self.request.get('password')
        self.session.delete_item('username')

        if id_ == '':
            doRender(self, 'login.html', {'error':'Please specify a username.'})
            return
        if pw == '':
            doRender(self, 'login.html', {'error':'Please specify a password.'})
            return
        
        user = Student.get_by_username(id_)
        if user is None:
            doRender(self,'login.html',{'error':'Invalid username entered. Please try again.  '})  
        elif pw == user.password:
            self.session['username'] = id_
            self.session['student_id'] = user.key().id()
            if user.isAdmin:
                self.session['admin'] = True
            self.redirect('/profile')
        else:
            doRender(self,'login.html',{'error':'Invalid password entered. Please try again.'})


class LogoutHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        self.session.delete_item('student_id')
        self.session.delete_item('admin')
        doRender(self,'index.html')


class ImportData(webapp.RequestHandler):
    def get(self):
        doRender(self,'import.html')

    def post(self):
        xml_string = self.request.get('xml-string')
        try:
            xmlImportString(xml_string)
        except Exception, e:
            doRender(self,'import.html',{ 'error' : e.args })
            # bug - was missing this return statement, so wound up
            # falling through to next redirect, and not realizing it was failing.
            return 
        self.redirect("/")


class ExportData(webapp.RequestHandler):
    def get(self):
        students = Student.all()
        xml = xmlExport(students)
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(xml)


class ClearData(webapp.RequestHandler):
    def get(self):
        """
        Clear the datastore
        """
        #. move this to utils
        # clear ALL the tables
        tables = [Student, Class, Book, Paper, Internship, Place, Game]
        tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
        for table in tables:
            query = table.all()
            db.delete(query)

        self.redirect("/")




_URLS = (
     ('/', MainPage),

     ('/login',LoginHandler),
     ('/logout',LogoutHandler),
     ('/signup',SignupHandler),
     #('/issueAccount', issueAccount),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/dbclear',ClearData),
     ('/about',About),
     ('/help',Help),

     ('/profile',StudentProfile),

     ('/changePassword', ChangePassword),

     ('/student/list', ListStudent),
     ('/student/delete', DeleteStudent),

     ('/class/list',ListClass),
     ('/class/add', AddClass),
     ('/class/view', ViewClass),
     ('/class/edit', EditClass),
     ('/class/delete', DeleteClass),

     ('/book/list', ListBook),
     ('/book/view', ViewBook),
     ('/book/add', AddBook),
     ('/book/edit', EditBook),
     ('/book/delete', DeleteBook),

     ('/paper/list', ListPaper),
     ('/paper/add', AddPaper),
     ('/paper/edit', EditPaper),
     ('/paper/delete', DeletePaper),
     ('/paper/view', ViewPaper),

     ('/internship/list', ListInternship),
     ('/internship/view', ViewInternship),
     ('/internship/add', AddInternship),
     ('/internship/edit', EditInternship),
     ('/internship/delete', DeleteInternship),

     ('/place/list', ListPlace),
     ('/place/add', AddPlace),
     ('/place/edit', EditPlace),
     ('/place/delete', DeletePlace),
     ('/place/view', ViewPlace),

     ('/game/list', ListGame),
     ('/game/add', AddGame),
     ('/game/edit', EditGame),
     ('/game/delete', DeleteGame),
     ('/game/view', ViewGame),
     )

def main():
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
