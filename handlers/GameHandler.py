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

# Game

class ListGame(webapp.RequestHandler):
    def get(self):
        games = Game.all()
        doRender(self,'game/list.html',{'games':games})

class AddGame(webapp.RequestHandler):
    def get(self):
        doRender(self,'game/add.html',{'form':GameForm()})

    def post(self):
        form = GameForm(data=self.request.POST)
        if form.is_valid():
	    try :
            	game = form.save()
            	self.redirect('/game/view?id=%d' % game.key().id())
	    except db.BadValueError, e:
		doRender(self,'game/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'game/add.html', form)

class EditGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        doRender(self,'game/add.html',{'form':GameForm(instance=game),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id)
        form = GameForm(data=self.request.POST, instance=game)
        if form.is_valid():
            entity = form.save()
            self.redirect('/game/list')
        else:
            doRender(self,'game/add.html', form)

class ViewGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        form = GameForm(instance=game)
        assocs = game.studentgame_set
        doRender(self,'game/view.html',{'form':form,'game':game,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        game_id = int(self.request.get('_id'))
        game = Game.get_by_id(game_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, place, rating, comment
        
        # add the assocation object
        assoc = StudentGame()
        assoc.student = student
        assoc.game = game
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        self.redirect("/game/list")

class DeleteGame(webapp.RequestHandler):
    def get(self):
        session = Session()
        id = int(self.request.get('id'))
        game = Game.get_by_id(id)
        doRender(self,'game/delete.html',{'game':game,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id).delete()
        self.redirect("/game/list")



