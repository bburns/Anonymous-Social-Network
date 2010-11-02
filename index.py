import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import djangoforms

from utils import xmlExport
from utils.xmlImport import xmlImportString
from utils.sessions import Session
from models import *
    
"""
ASN2
Anonymous Social Network phase 2
"""   

def doRender(handler,tname='index.html',values = {}):
    temp = os.path.join(
      os.path.dirname(__file__),
      'templates/' + tname)
    if not os.path.isfile(temp):
        return False

    newval = dict(values)
    newval['path'] = handler.request.path
    handler.session = Session()
    if 'username' in handler.session:
        newval['username'] = handler.session['username']

    outstr = template.render(temp,newval)
    handler.response.out.write(outstr)
    return True

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self,'index.html')

class LoginHandler(webapp.RequestHandler):
    def get(self):
        doRender(self,'login.html')

    def post(self):
        self.session = Session()
        acct = self.request.get('username')
        pw = self.request.get('password')
        self.session.delete_item('username')

        if pw == '' or acct == '':
            doRender(self,'login.html',{'error':'Please specify Username and Password'})
        elif pw =='secret':
            self.session['username'] = acct
            doRender(self,'index.html',{})
        else:
            doRender(self,'login.html',{'error':'Incorrect password'})

class LogoutHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        doRender(self,'index.html')

class SignupHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        doRender(self,'signup.html',{'form':UserForm()})

class ImportData(webapp.RequestHandler):
    def get(self):
        doRender(self,'import.html')

    def post(self):
        xml_file = self.request.get('xml-file')
        try:       
          xmlImportString(xml_file)
          self.redirect("/export")
        except Exception, e:
            doRender(self,'import.html',{ 'error' : e.args })

class ExportData(webapp.RequestHandler):
    def get(self):
        students = Student.all().fetch(1000)
        xml = xmlExport(students)
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(xml)

class ClearData(webapp.RequestHandler):
    def get(self):
        """
        Clear the datastore
        """
        query = Student.all()
        db.delete(query)
        self.redirect("/")

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        classes.fetch(100)
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        doRender(self,'class/add.html',{'form':ClassForm()})

    def post(self):
        form = ClassForm(self.request.POST)            
        form.save()
      	self.redirect("/class/list")

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

class ListBook(webapp.RequestHandler):
    def get(self):
        books = Book.all()
        doRender(self,'book/list.html',{'books': books})

class AddBook(webapp.RequestHandler):
    def get(self):
        doRender(self,'book/add.html',{'form':BookForm()})

    def post(self):
        data = BookForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            book = data.save() #(commit=False)
            book.put()
            self.redirect('/book/list')
        else:
            doRender(self,'book/add.html',data)

class EditBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        doRender(self,'book/add.html',{'form':BookForm(instance=book),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        #book = Book.get(db.Key.from_path('Book', id))
        book = Book.get_by_id(id)
        data = BookForm(data=self.request.POST, instance=book)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/book/list')
        else:
            doRender(self,'book/add.html',data)

class DeleteBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        #key = db.Key.from_path('Book', id)
        #book = Book.get(key)
        book = Book.get_by_id(id)
        book.delete()
        self.redirect('/book/list')

class ListPaper(webapp.RequestHandler):
    def get(self):
        papers = Paper.all()
        papers.fetch(100)
        doRender(self,'paper/list.html',{'papers':papers})

class AddPaper(webapp.RequestHandler):
    def get(self):
        doRender(self,'paper/add.html',{'form':PaperForm()})

    def post(self):
        data = PaperForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            paper = data.save() #(commit=False)
            paper.put()
            self.redirect('/paper/list')
        else:
            doRender(self,'paper/add.html',data)

class EditPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        doRender(self,'paper/add.html',{'form':PaperForm(instance=paper),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id)
        data = PaperForm(data=self.request.POST, instance=paper)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/paper/list')
        else:
            doRender(self,'paper/add.html',data)

class DeletePaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        paper = Paper.get_by_id(id)
        doRender(self,'paper/delete.html',{'paper':paper,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id).delete()
        self.redirect("/paper/list")

#Place
class ListPlace(webapp.RequestHandler):
    def get(self):
        places = Place.all()
        places.fetch(100)
        doRender(self,'place/list.html',{'places':places})

class AddPlace(webapp.RequestHandler):
    def get(self):
        doRender(self,'place/add.html',{'form':PlaceForm()})

    def post(self):
        data = PlaceForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            place = data.save() #(commit=False)
            place.put()
            self.redirect('/place/list')
        else:
            doRender(self,'place/add.html',data)

class EditPlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        place = Place.get_by_id(id)
        doRender(self,'place/add.html',{'form':PlaceForm(instance=place),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id)
        data = PlaceForm(data=self.request.POST, instance=place)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/place/list')
        else:
            doRender(self,'place/add.html',data)

class DeletePlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        place = Place.get_by_id(id)
        doRender(self,'place/delete.html',{'place':place,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id).delete()
        self.redirect("/place/list")

#Internship
class ListInternship(webapp.RequestHandler):
    def get(self):
        internships = Internship.all()
        internships.fetch(100)
        doRender(self,'internship/list.html',{'internships':internships})

class AddInternship(webapp.RequestHandler):
    def get(self):
        doRender(self,'internship/add.html',{'form':InternshipForm()})

    def post(self):
        data = InternshipForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            internship = data.save() #(commit=False)
            internship.put()
            self.redirect('/internship/list')
        else:
            doRender(self,'internship/add.html',data)

class EditInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        internship = Internship.get_by_id(id)
        doRender(self,'internship/add.html',{'form':InternshipForm(instance=internship),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id)
        data = InternshipForm(data=self.request.POST, instance=internship)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/internship/list')
        else:
            doRender(self,'internship/add.html',data)

class DeleteInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        internship = Internship.get_by_id(id)
        doRender(self,'internship/delete.html',{'internship':internship,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id).delete()
        self.redirect("/internship/list")

#Game
class ListGame(webapp.RequestHandler):
    def get(self):
        games = Game.all()
        games.fetch(100)
        doRender(self,'game/list.html',{'games':games})

class AddGame(webapp.RequestHandler):
    def get(self):
        doRender(self,'game/add.html',{'form':GameForm()})

    def post(self):
        data = GameForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            game = data.save() #(commit=False)
            game.put()
            self.redirect('/game/list')
        else:
            doRender(self,'game/add.html',data)

class EditGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        doRender(self,'game/add.html',{'form':GameForm(instance=game),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id)
        data = GameForm(data=self.request.POST, instance=game)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/game/list')
        else:
            doRender(self,'game/add.html',data)

class DeleteGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        game = Game.get_by_id(id)
        doRender(self,'game/delete.html',{'game':game,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id).delete()
        self.redirect("/game/list")


_URLS = (
     ('/', MainPage),

     ('/login',LoginHandler),
     ('/logout',LogoutHandler),
     ('/signup',SignupHandler),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/dbclear',ClearData),

     ('/class/add', AddClass),
     ('/class/edit', EditClass),
     ('/class/delete', DeleteClass),
     ('/class/list',ListClass),

     ('/book/list', ListBook),
     ('/book/add', AddBook),
     ('/book/edit', EditBook),
     ('/book/delete', DeleteBook),


     ('/paper/list', ListPaper),
     ('/paper/add', AddPaper),
     ('/paper/edit', EditPaper),
     ('/paper/delete', DeletePaper),

     ('/place/list', ListPlace),
     ('/place/add', AddPlace),
     ('/place/edit', EditPlace),
     ('/place/delete', DeletePlace),

     ('/internship/list', ListInternship),
     ('/internship/add', AddInternship),
     ('/internship/edit', EditInternship),
     ('/internship/delete', DeleteInternship),

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
