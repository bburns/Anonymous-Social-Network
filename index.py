import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import djangoforms

from xmlExport import xmlExport
from xmlImport import xmlImportString
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

    outstr = template.render(temp,newval)
    handler.response.out.write(outstr)
    return True

class MainPage(webapp.RequestHandler):
    """
    Request handler for main page (index.html). 
    """
    def get(self):
        doRender(self,'index.html')

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
        """
        Return the export page (export.html)
        """
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
        cl = Class.get(db.Key.from_path('Class', id))
        doRender(self,'class/add.html',{'form':ClassForm(instance=cl),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get(db.Key.from_path('Class', id))
        form = ClassForm(data = self.request.POST, instance = cl)
        form.save()
      	self.redirect("/class/list")

class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get(db.Key.from_path('Class', id))
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get(db.Key.from_path('Class', id)).delete()
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

class BookEdit(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        #key = db.Key.from_path('Book', id)
        #book = Book.get(key)
        self.response.out.write('<html><body>'
                                '<form method="POST" '
                                'action="/book/edit">'
                                '<table>')
        self.response.out.write(BookForm(instance=book))
        self.response.out.write('</table>'
                                '<input type="hidden" name="_id" value="%s">'
                                '<input type="submit">'
                                '</form></body></html>' % id)

    def post(self):
        id = int(self.request.get('_id'))
        #book = Book.get(db.Key.from_path('Book', id))
        book = Book.get_by_id(id)
        data = BookForm(data=self.request.POST, instance=book)
        if data.is_valid():
            # Save the data, and redirect to the view page
            entity = data.save(commit=False)
            # entity.added_by = users.get_current_user()
            entity.put()
            self.redirect('/book/list')
        else:
            # Reprint the form
            self.response.out.write('<html><body>'
                                    '<form method="POST" '
                                    'action="/book/edit">'
                                    '<table>')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="hidden" name="_id" value="%s">'
                                    '<input type="submit">'
                                    '</form></body></html>' % id)

class BookDelete(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        #key = db.Key.from_path('Book', id)
        #book = Book.get(key)
        book = Book.get_by_id(id)
        book.delete()
        self.redirect('/book/list')

_URLS = (
     ('/', MainPage),

     ('/export',ExportData),
     ('/import',ImportData),
     ('/dbclear',ClearData),

     ('/class/add', AddClass),
     ('/class/edit', EditClass),
     ('/class/delete', DeleteClass),
     ('/class/list',ListClass),

     ('/book/list', ListBook),
     ('/book/add', AddBook),
     ('/book/edit', BookEdit),
     ('/book/delete', BookDelete),
     )


def main():
    "Run the webapp"
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
