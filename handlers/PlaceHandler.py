import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
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

# Place

class ListPlace(webapp.RequestHandler):
    def get(self):
        places = Place.all()
        doRender(self,'place/list.html',{'places':places})

class AddPlace(webapp.RequestHandler):
    def get(self):
        doRender(self,'place/add.html',{'form':PlaceForm()})

    def post(self):
        form = PlaceForm(data=self.request.POST)
        if form.is_valid():
            try :
                place = form.save()
                id = place.key().id()
                self.redirect('/place/view?id=%d' % id)
            except db.BadValueError, e: 
                doRender(self,'place/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'place/add.html',{'form':form, 'error':'ERROR: please check the following and try again'})


class EditPlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        place = Place.get_by_id(id)
        doRender(self,'place/add.html',{'form':PlaceForm(instance=place),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id)
        form = PlaceForm(data=self.request.POST, instance=place)
        if form.is_valid():
            entity = form.save()  
            self.redirect('/place/list')
        else:
            doRender(self,'place/add.html', form)

class ViewPlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        place = Place.get_by_id(id)
        form = PlaceForm(instance=place)
        assocs = place.studentplace_set
        doRender(self,'place/view.html',{'form':form,'place':place,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        place_id = int(self.request.get('_id'))
        place = Place.get_by_id(place_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, place, rating, comment
        
        # add the assocation object
        assoc = StudentPlace()
        assoc.student = student
        assoc.place = place
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        self.redirect("/place/list")


class DeletePlace(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        place = Place.get_by_id(id)
        doRender(self,'place/delete.html',{'place':place,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        place = Place.get_by_id(id).delete()
        self.redirect("/place/list")
