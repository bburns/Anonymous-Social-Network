from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from utils.authenticate import *
from models import *

# Paper

class ListPaper(webapp.RequestHandler):
    def get(self):
        papers = Paper.all()
        doRender(self,'paper/list.html',{'papers':papers})

class AddPaper(webapp.RequestHandler):
    def get(self):
        doRender(self,'paper/add.html',{'form':PaperForm()})

    @authenticate
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
            doRender(self,'paper/add.html',{'form':form, \
                'error':'ERROR: Please correct the following errors and try again.'})


class EditPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        doRender(self,'paper/add.html',{'form':PaperForm(instance=paper),'id':id})

    @authenticate_admin
    def post(self):
        id = int(self.request.get('id'))
        paper = Paper.get_by_id(id)
        form = PaperForm(data=self.request.POST, instance=paper)
        if form.is_valid():
            try:
                form.save()
                self.redirect("/paper/list")
            except db.BadValueError, e:
                doRender(self, 'paper/add.html', {'form':form, 'id':id, 'error': "ERROR: " + e.args[0]})
        else:
            doRender(self,'paper/add.html',{'form':form, 'id':id, 'error':'ERROR: Please correct the following errors and try again.'})


class DeletePaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        paper = Paper.get_by_id(id)
        doRender(self,'paper/delete.html',{'paper':paper,'id':id})

    @authenticate_admin
    def post(self):
        id = int(self.request.get('_id'))
        paper = Paper.get_by_id(id)
        student_papers = StudentPaper.all().filter("paper = ", paper).fetch(1000)
        for student_paper in student_papers:
          student_paper.delete()
        paper.delete()
        self.redirect("/paper/list")

class ViewPaper(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        paper = Paper.get_by_id(id)
        form = PaperForm(instance=paper)
        assocs = paper.studentpaper_set

        self.session = Session()
        if not 'student_id' in self.session:
            sc = None
        else:
            student_id = self.session['student_id']
            student = Student.get_by_id(student_id)
            sc = StudentPaper.all().filter("student = ", student)
            sc = sc.filter("paper = ", paper)
            sc = sc.fetch(1) 
            if sc :
                sc = sc[0]
        doRender(self,'paper/view.html',{'form':form,'paper':paper,'assocs':assocs,'id':id, 'ratedThis' : sc})

    @authenticate
    def post(self):
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        paper_id = int(self.request.get('_id'))
        paper = Paper.get_by_id(paper_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        assoc = StudentPaper()
        assoc.student = student
        assoc.paper = paper
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        self.redirect("/paper/list")

class EditPaperLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentPaper.get_by_id(link_id)
        link_form = StudentPaperForm(instance=link)
        paper = link.paper
        doRender(self,'paper/editLink.html',{'link_form':link_form, 'paper':paper, 'link_id':link_id})

    @authenticate
    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentPaper.get_by_id(link_id)
        form = StudentPaperForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                paper = link.paper
                doRender(self, 'paper/editLink.html', {'link_form':form, 'paper':paper, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            paper = link.paper
            doRender(self,'paper/editLink.html',{'link_form':form, 'paper':paper, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})


