from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from utils.authenticate import *
from models import *

# Game

class ListGame(webapp.RequestHandler):
    def get(self):
        games = Game.all()
        doRender(self,'game/list.html',{'games':games})

class AddGame(webapp.RequestHandler):
    def get(self):
        doRender(self,'game/add.html',{'form':GameForm()})

    @authenticate
    def post(self):
        form = GameForm(data=self.request.POST)
        if form.is_valid():
            try :
                game = form.save()
                self.redirect('/game/view?id=%d' % game.key().id())
            except db.BadValueError, e:
                doRender(self,'game/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'game/add.html',{'form':form, \
                'error':'ERROR: Please correct the following errors and try again.'})

class EditBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        doRender(self,'book/add.html',{'form':BookForm(instance=book),'id':id})

    def post(self):
        id = int(self.request.get('id'))
        book = Book.get_by_id(id)   
        form = BookForm(data=self.request.POST, instance=book)
        if form.is_valid():
            try:
                form.save()
                self.redirect("/book/list")
            except db.BadValueError, e:
                doRender(self, 'book/add.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'book/add.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})



class EditGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        doRender(self,'game/add.html',{'form':GameForm(instance=game),'id':id})

    @authenticate_admin
    def post(self):
        id = int(self.request.get('id'))
        game = Game.get_by_id(id)
        form = GameForm(data=self.request.POST, instance=game)
        if form.is_valid():
            try:
                form.save()
                self.redirect("/game/list")
            except db.BadValueError, e:
                doRender(self, 'game/add.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'game/add.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})



class ViewGame(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        game = Game.get_by_id(id)
        form = GameForm(instance=game)
        assocs = game.studentgame_set

        self.session = Session()
        if not 'student_id' in self.session:
            sc = None
        else:
            student_id = self.session['student_id']
            student = Student.get_by_id(student_id)
            sc = StudentGame.all().filter("student = ", student)
            sc = sc.filter("game = ", game)
            sc = sc.fetch(1) 
            if sc :
                      sc = sc[0]        
        doRender(self,'game/view.html',{'form':form,'game':game,'assocs':assocs,'id':id, 'ratedThis' : sc})

    @authenticate
    def post(self):
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        game_id = int(self.request.get('_id'))
        game = Game.get_by_id(game_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

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

    @authenticate_admin
    def post(self):
        id = int(self.request.get('_id'))
        game = Game.get_by_id(id)
        student_games = StudentGame.all().filter("game = ",game).fetch(1000)
        for student_game in student_games:
            student_game.delete()
        game.delete()
        self.redirect("/game/list")

class EditGameLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentGame.get_by_id(link_id)
        link_form = StudentGameForm(instance=link)
        game = link.game
        doRender(self,'game/editLink.html',{'link_form':link_form, 'game':game, 'link_id':link_id})

    @authenticate
    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentGame.get_by_id(link_id)
        form = StudentGameForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                game = link.game
                doRender(self, 'game/editLink.html', {'link_form':form, 'game':game, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            game = link.game
            doRender(self,'game/editLink.html',{'link_form':form, 'game':game, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})
