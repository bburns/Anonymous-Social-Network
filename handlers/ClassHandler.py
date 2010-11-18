from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from utils.authenticate import *
from models import *

# Class

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        doRender(self,'class/list.html',{'classes':classes})

class AddClass(webapp.RequestHandler):
    def get(self):
        form = ClassForm()
        doRender(self,'class/add.html',{'form':form})

    @authenticate
    def post(self):
        form = ClassForm(self.request.POST)
        if form.is_valid(): # checks values with validation functions
            try:
                cl = form.save() # this calls Class.put(), which checks for missing values
                self.redirect("/class/view?id=%d" % cl.key().id())
            except db.BadValueError, e:
                doRender(self,'class/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'class/add.html',{'form':form, \
                'error':'ERROR: Please correct the following errors and try again.'})

class EditClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/add.html',{'form':ClassForm(instance=cl),'id':id})

    @authenticate_admin
    def post(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        form = ClassForm(data = self.request.POST, instance = cl)
        if form.is_valid():
           try:
            form.save()
            self.redirect("/class/list")
           except db.BadValueError, e:
            doRender(self, 'class/add.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/add.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})
       
class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    @authenticate_admin
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

        self.session = Session()
        if not 'student_id' in self.session:
            sc = None
        else:
            student_id = self.session['student_id']
            student = Student.get_by_id(student_id)
            sc = StudentClass.all().filter("student = ", student)
            sc = sc.filter("class_ = ", class_)
            sc = sc.fetch(1) 
            if sc :
                      sc = sc[0]        
        doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'links':links,'id':class_id, 'ratedThis' : sc})
    

    @authenticate
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
                links = class_.studentclass_set
                doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'links':links,'id':class_id,\
                    'error': "ERROR: " + e.args[0]})
        else :
            links = class_.studentclass_set
            doRender(self,'class/view.html',{'link_form':link_form,'class':class_,'links':links,'id':class_id,\
                'error':'ERROR: Please correct the following errors and try again.'})

class EditClassLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentClass.get_by_id(link_id)
        link_form = StudentClassForm(instance=link)
        class_ = link.class_
        doRender(self,'class/editLink.html',{'link_form':link_form, 'class':class_, 'link_id':link_id})

    @authenticate
    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentClass.get_by_id(link_id)
        form = StudentClassForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                class_ = link.class_
                doRender(self, 'class/editLink.html', {'link_form':form, 'class':class_, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            class_ = link.class_
            doRender(self,'class/editLink.html',{'link_form':form, 'class':class_, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})
