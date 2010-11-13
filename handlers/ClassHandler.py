import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *

# Class

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        # classes.fetch(100)  # Class.all() can be iterated over. 
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        id = self.session['student_id']
        doRender(self,'class/add.html',{'class_form':ClassForm(), 'studentclass_form':StudentClassForm(),'id':id})

    def post(self):
        class_form = ClassForm(self.request.POST)
        sc_form = StudentClassForm(self.request.POST)
        student = Student.get_by_id(int(self.request.get('id')))
        if class_form.is_valid() and sc_form.is_valid() :
            try :
                cl = class_form.save()
                sc = sc_form.save(commit = False)
                sc.student = student
                sc.class_ = cl
                sc.put()
                self.redirect("/class/list")
            except db.BadValueError, e :
                doRender(self,'class/add.html',{'class_form':class_form, \
                'studentclass_form':sc_form, 'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/add.html',{'class_form':class_form, \
            'studentclass_form':sc_form, 'error':'ERROR: Please correct the following errors and try again.'})
		


class EditClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/add.html',{'form':ClassForm(instance=cl),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id)
        form = ClassForm(data = self.request.POST, instance = cl)
	if form.is_valid() :
	   try :
		form.save()
		self.redirect("/class/list")
	   except db.BadValueError, e :
		doRender(self, 'class/edit.html', {'form':form, 'error': "ERROR: " + e.args[0]})
	else :
		doRender(self,'class/edit.html',{'form':form, 'error':'ERROR: Please correct the following errors and try again.'})
	       

class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id).delete()
        self.redirect("/class/list")

class ViewClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        class_ = Class.get_by_id(id)
        form = ClassForm(instance=class_)
        assocs = class_.studentclass_set
        doRender(self,'class/view.html',{'form':form,'class':class_,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        class_id = int(self.request.get('_id'))
        class_ = Class.get_by_id(class_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        
        # add the assocation object
        assoc = StudentClass()
        assoc.student = student
        assoc.class_ = class_
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        #self.redirect("/book/view?id=%d" % book_id)
        self.redirect("/class/list")


