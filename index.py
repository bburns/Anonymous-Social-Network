
"""
ASN2
Anonymous Social Network phase 2
"""   

import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import djangoforms

from utils.xmlExport import xmlExport
from utils.xmlImport import xmlImportString
from utils.sessions import Session
from models import *

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self,'index.html')

class Help(webapp.RequestHandler):
    def get(self):
        doRender(self,"help.html")

class About(webapp.RequestHandler):
    def get(self):
        doRender(self,"about.html")

class StudentProfile(webapp.RequestHandler):
    def get(self):
        doRender(self,"profile.html")


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
            email = self.request.get('email')
            if User.get_by_email(email):
                doRender(self,'signup.html',{'error': "Sorry, that username already exists. Please try another one."})
                return
            s = Student()
            s.generateID()
            s.password = self.request.get('password')
            s.put()
            user = form.save()
            user.student = s
            user.put()
            self.session['username'] = user.email
            self.session['student_id'] = s.key().id()
            self.redirect('/')
        else:
            doRender(self,'signup.html', {'error': "Could not process the information please check the following and try again: <br/>- all the fields are filled in. <br/>- valid email address entered."})


class LoginHandler(webapp.RequestHandler):
    def get(self):
        doRender(self,'login.html')

    def post(self):
        self.session = Session()
        email = self.request.get('username')
        pw = self.request.get('password')
        self.session.delete_item('username')

        if email == '':
            doRender(self, 'login.html', {'error':'Please specify a username.'})
            return
        if pw == '':
            doRender(self, 'login.html', {'error':'Please specify a password.'})
            return
        
        user = User.get_by_email(email)
    
        if user is None:
            doRender(self,'login.html',{'error':'Invalid username or password entered. Please try again.'})  
        elif pw == user.password:
            self.session['username'] = email
            if user.student != None:
                self.session['student_id'] = user.student.key().id()
            if user.isAdmin:
                self.session['admin'] = True
            self.redirect('/')
        else:
            doRender(self,'login.html',{'error':'Invalid username or password entered. Please try again.'})


class LogoutHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        self.session.delete_item('student_id')
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


# Class

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        # classes.fetch(100)  # Class.all() can be iterated over. 
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        doRender(self,'class/add.html',{'form':ClassForm()})

    def post(self):
        form = ClassForm(self.request.POST)
	if form.is_valid() :
	        form.save()
        	self.redirect("/class/list")
	else :
		doRender(self,'class/add.html',{'form':form, 'error':'ERROR: Please correct the following errors and try again.'})
		


class EditClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/add.html',{'form':ClassForm(instance=cl),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id)
        form = ClassForm(data = self.request.POST, instance = cl)
        form.save()
        self.redirect("/class/list")

class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id).delete()
        self.redirect("/class/list")


# Book

# also want to show ratings and comments.
# maybe show avg rating, # of ratings in listing. 
# click on a book to view it, and all associated ratings and comments


class ListBook(webapp.RequestHandler):
    def get(self):
        books = Book.all()
        doRender(self,'book/list.html',{'books': books})

class ViewBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        form = BookForm(instance=book)
        assocs = book.studentbook_set
        doRender(self,'book/view.html',{'form':form,'book':book,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        book_id = int(self.request.get('_id'))
        book = Book.get_by_id(book_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        
        # add the assocation object
        assoc = StudentBook()
        assoc.student = student
        assoc.book = book
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        self.redirect("/book/view?id=%d" % book_id)
        

class AddBook(webapp.RequestHandler):
    def get(self):
        doRender(self,'book/add.html',{'form':BookForm()})

    def post(self):
        form = BookForm(data=self.request.POST)
        if form.is_valid():
            book = form.save()
            id = book.key().id()
            self.redirect('/book/view?id=%d' % id)
        else:
            doRender(self,'book/add.html', form)

class EditBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        doRender(self,'book/edit.html',{'form':BookForm(instance=book),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        book = Book.get_by_id(id)
        form = BookForm(data=self.request.POST, instance=book)
        if form.is_valid():
            form.save
            #self.redirect('/book/list')
            self.redirect('/book/view?id=%d' % id)
        else:
            doRender(self,'book/edit.html', form) # so presumably form acts as a dictionary...

class DeleteBook(webapp.RequestHandler):
    
    def get(self):
        id = int(self.request.get('id'))
        book = Book.get_by_id(id)
        doRender(self,'book/delete.html',{'book':book, 'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        book = Book.get_by_id(id)
        book.delete()
        self.redirect("/book/list")



# Paper

class ListPaper(webapp.RequestHandler):
    def get(self):
        papers = Paper.all()
        doRender(self,'paper/list.html',{'papers':papers})

class AddPaper(webapp.RequestHandler):
    def get(self):
        doRender(self,'paper/add.html',{'form':PaperForm()})

    def post(self):
        form = PaperForm(data=self.request.POST)
        if form.is_valid():
            #self.response.out.write("valid data")
            paper = form.save()
            self.redirect('/paper/list')
        else:
            doRender(self,'paper/add.html', form)

class EditPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        doRender(self,'paper/add.html',{'form':PaperForm(instance=paper),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id)
        form = PaperForm(data=self.request.POST, instance=paper)
        if form.is_valid():
            paper = form.save()
            self.redirect('/paper/list')
        else:
            doRender(self,'paper/add.html', form)

class DeletePaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        paper = Paper.get_by_id(id)
        doRender(self,'paper/delete.html',{'paper':paper,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id).delete()
        self.redirect("/paper/list")


# Place

class ListPlace(webapp.RequestHandler):
    def get(self):
        places = Place.all()
        doRender(self,'place/list.html',{'places':places})

class AddPlace(webapp.RequestHandler):
    def get(self):
        doRender(self,'place/add.html',{'form':PlaceForm()})

    def post(self):
        form = PlaceForm(data=self.request.POST)
        if form.is_valid():
            place = data.save()
            self.redirect('/place/list')
        else:
            doRender(self,'place/add.html', form)

class EditPlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        place = Place.get_by_id(id)
        doRender(self,'place/add.html',{'form':PlaceForm(instance=place),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id)
        form = PlaceForm(data=self.request.POST, instance=place)
        if form.is_valid():
            entity = form.save()
            self.redirect('/place/list')
        else:
            doRender(self,'place/add.html', form)

class DeletePlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        place = Place.get_by_id(id)
        doRender(self,'place/delete.html',{'place':place,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id).delete()
        self.redirect("/place/list")


# Internship
class ListInternship(webapp.RequestHandler):
    def get(self):
        internships = Internship.all()
        doRender(self,'internship/list.html',{'internships':internships})



class ViewInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        internship = Internship.get_by_id(id)
        form = InternshipForm(instance=internship)
        assocs = internship.studentinternship_set
        doRender(self,'internship/view.html',{'form':form,'internship':internship,'assocs':assocs,'id':id})

    def post(self):

        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        internship_id = int(self.request.get('_id'))
        internship = Internship.get_by_id(internship_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        # add the assocation object
        assoc = StudentInternship()
        assoc.student = student
        assoc.internship = internship
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        #self.redirect("/internship/view?id=%d" % internship_id)
        self.redirect("/internship/list")


class AddInternship(webapp.RequestHandler):
    def get(self):
        doRender(self,'internship/add.html',{'form':InternshipForm()})

    def post(self):
        form = InternshipForm(data=self.request.POST)
        if form.is_valid():
            internship = form.save()
            id = internship.key().id()
            self.redirect('/internship/view?id=%d' % id)
        else:
            doRender(self,'internship/add.html',form)

class EditInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        internship = Internship.get_by_id(id)
        doRender(self,'internship/edit.html',{'form':InternshipForm(instance=internship),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id)
        form = InternshipForm(data=self.request.POST, instance=internship)
        if form.is_valid():
            form.save()
            #self.redirect('/internship/list')
            self.redirect('/internship/view?id=%d' % id)
        else:
            doRender(self,'internship/edit.html', form)

class DeleteInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        internship = Internship.get_by_id(id)
        doRender(self,'internship/delete.html',{'internship':internship,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id)
        internship.delete()
        self.redirect("/internship/list")

#Game
class ListGame(webapp.RequestHandler):
    def get(self):
        games = Game.all()
        doRender(self,'game/list.html',{'games':games})

class AddGame(webapp.RequestHandler):
    def get(self):
        doRender(self,'game/add.html',{'form':GameForm()})

    def post(self):
        form = GameForm(data=self.request.POST)
        if form.is_valid():
            game = data.save()
            self.redirect('/game/list')
        else:
            doRender(self,'game/add.html', form)

class EditGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        doRender(self,'game/add.html',{'form':GameForm(instance=game),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id)
        form = GameForm(data=self.request.POST, instance=game)
        if form.is_valid():
            entity = form.save()
            self.redirect('/game/list')
        else:
            doRender(self,'game/add.html', form)

class DeleteGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        game = Game.get_by_id(id)
        doRender(self,'game/delete.html',{'game':game,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id).delete()
        self.redirect("/game/list")



def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), 'templates/' + filename)
    if not os.path.isfile(filepath):
        self.response.out.write("Invalid template file: " + filename)
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
    #.
    newdict['admin'] = True


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

     ('/class/list',ListClass),
     ('/class/add', AddClass),
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

     ('/internship/list', ListInternship),
     ('/internship/view', ViewInternship),
     ('/internship/add', AddInternship),
     ('/internship/edit', EditInternship),
     ('/internship/delete', DeleteInternship),

     ('/place/list', ListPlace),
     ('/place/add', AddPlace),
     ('/place/edit', EditPlace),
     ('/place/delete', DeletePlace),

     ('/game/list', ListGame),
     ('/game/add', AddGame),
     ('/game/edit', EditGame),
     ('/game/delete', DeleteGame),
     )


def main():
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
