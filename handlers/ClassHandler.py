import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *

# Class

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        student_id = self.session['student_id']
        doRender(self,'class/add.html',{'class_form':ClassForm(), 'id':student_id})

    def post(self):
        student_id = int(self.request.get('id'))
        class_form = ClassForm(self.request.POST)
        if class_form.is_valid(): 
            try :
                cl = class_form.save() # this calls Class.put(), which checks for missing values
                self.redirect("/class/view?id=%d" % cl.key().id())
            except db.BadValueError, e :
                doRender(self,'class/add.html',{'class_form':class_form, \
                'id':student_id, 'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/add.html',{'class_form':class_form, \
            'id':student_id, 'error':'ERROR: Please correct the following errors and try again.'})



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
            doRender(self, 'class/edit.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/edit.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})
       

class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id)
        student_classes = StudentClass.all().filter("class_ = ",cl).fetch(1000)
        for student_class in student_classes:
            student_class.delete()
        cl.delete()
        self.redirect("/class/list")



class ViewClass(webapp.RequestHandler):
    def get(self):
        class_id = int(self.request.get('id')) # get id from "?id=" in url
        class_ = Class.get_by_id(class_id)
        link_form = StudentClassForm()
        links = class_.studentclass_set
        doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'assocs':links,'id':class_id})

    def post(self):

        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        class_id = int(self.request.get('_id'))
        class_ = Class.get_by_id(class_id)

        link_form = StudentClassForm(self.request.POST)
        if link_form.is_valid() :
            try :
                link = link_form.save(commit = False)
                link.student = student
                link.class_ = class_
                link.put()
                self.redirect("/class/list")
            except db.BadValueError, e :
                doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'assocs':assocs,'id':class_id,\
                    'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'assocs':assocs,'id':class_id,\
                'error':'ERROR: Please correct the following errors and try again.'})


