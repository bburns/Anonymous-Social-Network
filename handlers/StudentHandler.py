import os
from google.appengine.ext import webapp
from utils.doRender import doRender
from utils.sessions import Session
from models import *

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

