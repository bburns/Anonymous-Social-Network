import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *

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
            try :
            	internship = form.save()
            	id = internship.key().id()
            	self.redirect('/internship/view?id=%d' % id)
            except db.BadValueError, e :
                doRender(self,'internship/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'internship/add.html',{'form':form, \
                'error':'ERROR: Please correct the following errors and try again.'})


class EditInternship(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        internship = Internship.get_by_id(id)
        doRender(self,'internship/add.html',{'form':InternshipForm(instance=internship),'id':id})

    def post(self):
        id = int(self.request.get('id'))
        internship = Internship.get_by_id(id)
        form = InternshipForm(data=self.request.POST, instance=internship)
        if form.is_valid():
            try:
                form.save()
                self.redirect("/internship/list")
            except db.BadValueError, e:
                doRender(self, 'internship/add.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'internship/add.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})


class DeleteInternship(webapp.RequestHandler):
    def get(self):  
        id = int(self.request.get('id'))
        internship = Internship.get_by_id(id)
        doRender(self,'internship/delete.html',{'internship':internship,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id)
        student_internships = StudentInternship.all().filter("internship = ", internship).fetch(1000)
        for student_internship in student_internships:
          student_internship.delete()
        internship.delete()
        self.redirect("/internship/list")





class EditInternshipLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentInternship.get_by_id(link_id)
        link_form = StudentInternshipForm(instance=link)
        internship = link.internship
        doRender(self,'internship/editLink.html',{'link_form':link_form, 'internship':internship, 'link_id':link_id})

    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentInternship.get_by_id(link_id)
        form = StudentInternshipForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                internship = link.internship
                doRender(self, 'internship/editLink.html', {'link_form':form, 'internship':internship, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            internship = link.internship
            doRender(self,'internship/editLink.html',{'link_form':form, 'internship':internship, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})

