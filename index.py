
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
from models import *
from handlers import *
# from handlers.ClassHandler import * 
# from handlers.BookHandler import *
# from handlers.PaperHandler import *
# from handlers.PlaceHandler import *
# from handlers.InternshipHandler import *
# from handlers.GameHandler import *
# from handlers.StudentHandler import *

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


class changePassword(webapp.RequestHandler):
    def get(self):
        x = Session()  
        if 'student_id' in x:      
            s = Student.get_by_id(x['student_id'])

        doRender(self,'changePassword.html',{})

    def post(self):
        template = {}	
        self.session = Session()
            oldPass = self.request.get('oldPass')
            newPass1 = self.request.get('newPass1')
            newPass2 = self.request.get('newPass2')
        username = self.session['username']
        user = Student.get_by_id(username)
        if(oldPass != user.password):
            template['oldPassError'] = True

        if( newPass1 != newPass2):
            template['mismatch'] = True

        if(oldPass == user.password and newPass1 == newPass2):
            user.password = newPass1
            user.put()
            template['success'] = True
        doRender(self,'changePassword.html', template)


class SignupHandler(webapp.RequestHandler):
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
            if Student.get_by_id(username):
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


class LoginHandler(webapp.RequestHandler):
    def get(self):
        doRender(self,'login.html')

    def post(self):
        self.session = Session()
        #email = self.request.get('username')
        id_ = self.request.get('username')        
        pw = self.request.get('password')
        self.session.delete_item('username')

        if id_ == '':        # if email == ' ' :
            doRender(self, 'login.html', {'error':'Please specify a username.'})
            return
        if pw == '':
            doRender(self, 'login.html', {'error':'Please specify a password.'})
            return
        
        # user = User.get_by_email(email)
        user = Student.get_by_id(id_)
        if user is None:
            doRender(self,'login.html',{'error':'Invalid username entered. Please try again.  '})  
        elif pw == user.password:
            self.session['username'] = id_
            self.session['student_id'] = user.key().id()
            if user.isAdmin:
                self.session['admin'] = True
            self.redirect('/')
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
        # xml_file = self.request.get('xml-file')
        xml_string = self.request.get('xml-string')
        # print self.request
        try:
            # if xml_file:
                # xmlImportString(xml_file)
            # else:
                # xmlImportString(xml_string)
            xmlImportString(xml_string)
        except Exception, e:
            doRender(self,'import.html',{ 'error' : e.args })
        self.redirect("/")


class ExportData(webapp.RequestHandler):
    def get(self):
        students = Student.all()  #.fetch(1000)  can just iterate over all()
        xml = xmlExport(students)
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(xml)


class ClearData(webapp.RequestHandler):
    def get(self):
        """
        Clear the datastore
        """
        # query = Student.all()
        # db.delete(query)
        # self.redirect("/")

        #. move this to utils
        # clear ALL the tables
        tables = [Student, Class, Book, Paper, Internship, Place, Game]
        tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
        for table in tables:
            query = table.all()
            db.delete(query)

        self.redirect("/")


def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), 'views/' + filename)
    if not os.path.isfile(filepath):
        handler.response.out.write("Invalid template file: " + filename)
        return False

    # copy the dictionary, so we can add things to it
    newdict = dict(values)
    newdict['path'] = handler.request.path
    newdict['recentClasses'] = Class.get_by_date()
    newdict['recentBooks'] = Book.get_by_date()
    newdict['recentPapers'] = Paper.get_by_date()
    newdict['recentInternships'] = Internship.get_by_date()
    newdict['recentPlaces'] = Place.get_by_date()
    newdict['recentGames'] = Game.get_by_date()

    handler.session = Session()
    if 'username' in handler.session:
        newdict['username'] = handler.session['username']

    if 'student_id' in handler.session:
        newdict['student_id'] = handler.session['student_id']
    
    if 'admin' in handler.session:
        newdict['admin'] = handler.session['admin']

    s = template.render(filepath, newdict)
    handler.response.out.write(s)
    return True


_URLS = (
     ('/', MainPage),

     ('/login',LoginHandler),
     ('/logout',LogoutHandler),
     ('/signup',SignupHandler),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/dbclear',ClearData),
     ('/about',About),
     ('/help',Help),

     ('/profile',StudentProfile),

     ('/changePassword', changePassword),

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
