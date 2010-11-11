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

# Paper

class ListPaper(webapp.RequestHandler):
    def get(self):
        papers = Paper.all()
        doRender(self,'paper/list.html',{'papers':papers})

class AddPaper(webapp.RequestHandler):
    def get(self):
        doRender(self,'paper/add.html',{'form':PaperForm()})

    def post(self):
        form = PaperForm(data=self.request.POST)
        if form.is_valid():
            try :
                paper = form.save()
                id = paper.key().id()
                self.redirect('/paper/view?id=%d' % id)
            except db.BadValueError, e:
                doRender(self,'paper/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'paper/add.html', {'form':form})

class EditPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        doRender(self,'paper/add.html',{'form':PaperForm(instance=paper),'id':id})

    def post(self):
        id = int(self.request.get('_id'))  
        paper = Paper.get_by_id(id)
        form = PaperForm(data=self.request.POST, instance=paper)
        if form.is_valid():
            paper = form.save()
            self.redirect('/paper/list')
        else:
            doRender(self,'paper/add.html', form)

class DeletePaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        paper = Paper.get_by_id(id)
        doRender(self,'paper/delete.html',{'paper':paper,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id).delete()
        self.redirect("/paper/list")

class ViewPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        form = PaperForm(instance=paper)
        assocs = paper.studentpaper_set
        doRender(self,'paper/view.html',{'form':form,'paper':paper,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        paper_id = int(self.request.get('_id'))
        paper = Paper.get_by_id(paper_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        
        # add the assocation object
        assoc = StudentPaper()
        assoc.student = student
        assoc.paper = paper
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        #self.redirect("/book/view?id=%d" % book_id)
        self.redirect("/paper/list")
