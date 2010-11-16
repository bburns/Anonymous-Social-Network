import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *

# Place

class ListPlace(webapp.RequestHandler):
    def get(self):
        places = Place.all()
        doRender(self,'place/list.html',{'places':places})

class AddPlace(webapp.RequestHandler):
    def get(self):
        doRender(self,'place/add.html',{'form':PlaceForm()})

    def post(self):
        place = Place(place_type=self.request.get("id_place_type"))
        form = PlaceForm(data=self.request.POST,instance=place)
        if form.is_valid(): # this checks the values against the validator functions
            try :
                place = form.save() # this calls Place.put(), which checks for missing values
                place_id = place.key().id()
                self.redirect('/place/view?id=%d' % place_id)
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
        place = Place.get_by_id(id)
        student_places = StudentPlace.all().filter("place = ", place).fetch(1000)
        for student_place in student_places:
          student_place.delete()
        place.delete()
        self.redirect("/place/list")





class EditPlaceLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentPlace.get_by_id(link_id)
        link_form = StudentPlaceForm(instance=link)
        place = link.place
        doRender(self,'place/editLink.html',{'link_form':link_form, 'place':place, 'link_id':link_id})

    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentPlace.get_by_id(link_id)
        form = StudentPlaceForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                place = link.place
                doRender(self, 'place/editLink.html', {'link_form':form, 'place':place, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            place = link.place
            doRender(self,'place/editLink.html',{'link_form':form, 'place':place, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})

