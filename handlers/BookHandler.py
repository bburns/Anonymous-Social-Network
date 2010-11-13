import os
from google.appengine.ext import webapp
from utils.sessions import Session
from utils.doRender import doRender
from models import *

# Book

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
        doRender(self,'book/view.html',{'form':form,'book':book,'assocs':assocs,'id':id})

    def post(self):
        self.session = Session()
        if 'student_id' in self.session:
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
        else:
            doRender(self,'not_auth.html')

class AddBook(webapp.RequestHandler):
    def get(self):
        doRender(self,'book/add.html',{'form':BookForm()})

    def post(self):
        self.session = Session()
        if 'student_id' in self.session:
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
        else:
            doRender(self,'not_auth.html')

class EditBook(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        doRender(self,'book/edit.html',{'form':BookForm(instance=book),'id':id})

    def post(self):
        self.session = Session()
        if 'student_id' in self.session:
            id = int(self.request.get('_id'))
            book = Book.get_by_id(id)   
            form = BookForm(data=self.request.POST, instance=book)
            if form.is_valid():
                form.save
                self.redirect('/book/view?id=%d' % id)
            else:
                doRender(self,'book/edit.html', {'form': form})
        else:
            doRender(self,'not_auth.html')

class DeleteBook(webapp.RequestHandler):
    
    def get(self):
        id = int(self.request.get('id'))
        book = Book.get_by_id(id)
        doRender(self,'book/delete.html',{'book':book, 'id':id})

    def post(self):
        self.session = Session()
        if 'student_id' in self.session:
            id = int(self.request.get('_id'))
            book = Book.get_by_id(id)
            book.delete()
            self.redirect("/book/list")
        else:
            doRender(self,'not_auth.html')
