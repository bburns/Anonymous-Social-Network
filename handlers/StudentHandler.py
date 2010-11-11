import os
from google.appengine.ext import webapp
from utils.sessions import Session
from models import *

def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), '../templates/' + filename)
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

class StudentProfile(webapp.RequestHandler):
    def get(self):
        x = Session()
        if 'student_id' in x:
            template = {}
            sb = StudentBook.all()
            sc = StudentClass.all()
            sp = StudentPlace.all()
            si = StudentInternship.all()
            spa = StudentPaper.all()
            sg = StudentGame.all()
            
            s = Student.get_by_id(x['student_id'])
            
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

class DeleteStudent(webapp.RequestHandler):
    
    def get(self):
        id = int(self.request.get('id'))
        student = Student.get_by_id(id)
        doRender(self,'student/delete.html',{'student':student, 'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        student = Student.get_by_id(id)
        student.delete()
        self.redirect("/student/list")

