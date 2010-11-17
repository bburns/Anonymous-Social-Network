from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from utils.authenticate import *
from models import *

class ListBook(webapp.RequestHandler):
    def get(self):
        books = Book.all()
        doRender(self,'book/list.html',{'books': books})

class ViewBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        form = BookForm(instance=book)
        assocs = book.studentbook_set

	self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)
        sb = StudentBook.all().filter("student = ", student)
	sb = sb.filter("book = ", book)
	sb = sb.fetch(1) 
	if sb :
              sb = sb[0]        
        doRender(self,'book/view.html',{'form':form,'book':book,'assocs':assocs,'id':id, 'ratedThis' : sb})


    @authenticate
    def post(self):
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)
        book_id = int(self.request.get('_id'))
        book = Book.get_by_id(book_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        
        # add the assocation object
        assoc = StudentBook()
        assoc.student = student
        assoc.book = book
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        #self.redirect("/book/view?id=%d" % book_id)
        self.redirect("/book/list")

class AddBook(webapp.RequestHandler):
    def get(self):
        doRender(self,'book/add.html',{'form':BookForm()})

    @authenticate
    def post(self):
        self.session = Session()
        form = BookForm(data=self.request.POST)
        if form.is_valid():
            try :
                book = form.save()
                id = book.key().id()
                self.redirect('/book/view?id=%d' % id)
            except db.BadValueError, e :
                doRender(self,'book/add.html',{'form':form, 'error':"ERROR: " + e.args[0]})
        else:
            doRender(self,'book/add.html',{'form': form, 'error': 'ERROR: please check the following and try again'})

class EditBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        doRender(self,'book/edit.html',{'form':BookForm(instance=book),'id':id})

    @authenticate_admin
    def post(self):
        self.session = Session()
        id = int(self.request.get('_id'))
        book = Book.get_by_id(id)   
        form = BookForm(data=self.request.POST, instance=book)
        if form.is_valid():
            form.save
            self.redirect('/book/view?id=%d' % id)
        else:
            doRender(self,'book/edit.html', {'form': form})

class DeleteBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        book = Book.get_by_id(id)
        doRender(self,'book/delete.html',{'book':book, 'id':id})

    @authenticate_admin
    def post(self):
        self.session = Session()
        id = int(self.request.get('_id'))
        book = Book.get_by_id(id)
        student_books = StudentBook.all().filter("book = ",book).fetch(1000)
        for student_book in student_books:
            student_book.delete()
        book.delete()
        self.redirect("/book/list")

class EditBookLink(webapp.RequestHandler):
    def get(self):
        # get from ?link_id= in url, or hidden form field
        link_id = int(self.request.get('link_id')) 
        link = StudentBook.get_by_id(link_id)
        link_form = StudentBookForm(instance=link)
        book = link.book
        doRender(self,'book/editLink.html',{'link_form':link_form, 'book':book, 'link_id':link_id})

    @authenticate
    def post(self):
        link_id = int(self.request.get('link_id'))
        link = StudentBook.get_by_id(link_id)
        form = StudentBookForm(data = self.request.POST, instance = link)
        if form.is_valid(): # this checks values against validation functions
            try: 
                link = form.save() # this calls put, which checks for missing values
                self.redirect("/profile")
            except db.BadValueError, e:
                book = link.book
                doRender(self, 'book/editLink.html', {'link_form':form, 'book':book, 'link_id':link_id, 'error': "ERROR: " + e.args[0]})
        else:
            book = link.book
            doRender(self,'book/editLink.html',{'link_form':form, 'book':book, 'link_id':link_id, 'error':'ERROR: Please correct the following errors and try again.'})

