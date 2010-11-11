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
            doRender(self,'internship/add.html',{'form':form})

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
        internship = Internship.get_by_id(id)
        doRender(self,'internship/delete.html',{'internship':internship,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        internship = Internship.get_by_id(id)
        internship.delete()
        self.redirect("/internship/list")



