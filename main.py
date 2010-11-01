import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.ext.db import djangoforms

from xml.dom import minidom
from xmlExport import xmlExport
from xmlImport import xmlImportString
#from models import Student
from models import *
    
"""
ASN1
Anonymous Social Network phase 1
"""   

class MainPage(webapp.RequestHandler):
    """
    Request handler for main page (index.html). 
    """
    def get(self):
        """
        Return the main page (index.html)
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'index.html')
        self.response.out.write(template.render(path, template_values, True))

class ImportData(webapp.RequestHandler):
    def get(self):
        """
        Return the import page (import.html).
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'import.html')
        self.response.out.write(template.render(path, template_values, True))

    def post(self):
        """
        Get xml data from the text box and import then redirect to export
        """
        xml_file = self.request.get('xml-file')
        try:       
          xmlImportString(xml_file)
          self.redirect("/export")
        except Exception, e:
            template_values = { 'error' : e.args }
            directory = os.path.dirname(__file__)
            path = os.path.join(directory, 'import.html')
            self.response.out.write(template.render(path, template_values, True))

         
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


class BookForm(djangoforms.ModelForm):
    class Meta:
        model = Book
        # exclude = ['isbn']

class BookData(webapp.RequestHandler):
    def get(self):
       self.response.out.write('<html><body>'
                                '<form method="post" '
                                'action="/book">'
                                '<table>')
       # This generates our shopping list form and writes it in the response
       self.response.out.write(BookForm())
       self.response.out.write('</table>'
                                '<input type="submit">'
                                '</form></body></html>')        
    def post(self):
        self.response.out.write("eriwrueiru")
        data = BookForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            # Save the data, and redirect to the view page
            book = data.save() #(commit=False)
            #book.added_by = users.get_current_user()
            book.put()
            self.response.out.write("hello")
            self.redirect('/book')
            # self.response.out.write("Successfully Added:" + book.title)
        else:
            # Reprint the form
            self.response.out.write('<html><body>'
                                    '<form method="post" '
                                    'action="/book">'
                                    '<table>jlijlijlij')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="submit">'
                                    '</form></body></html>')




_URLS = (
     ('/', MainPage),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/book', BookData),
     ('/dbclear',ClearData)
     )

def main():
    "Run the webapp"
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
