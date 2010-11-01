from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

class Student(db.Model):

    id_ = db.StringProperty()   # id is reserved in python
    password = db.StringProperty()

    #. init - generate random password


    # for phase 2
    def addBook(self, title, author='', isbn='', rating=None, comment=''):
        """
        Add the given book as a related object for this student. 
        Creates the book if it can't find it in the database.
        """
        sb = StudentBook()
        sb.student = self
        sb.book = findAddBook(title, author, isbn)
        sb.rating = rating
        sb.comment = comment
        sb.put()

class Class(db.Model):
    unique = db.StringProperty()
    course_num = db.StringProperty()
    semester = db.StringProperty()
    instructor = db.StringProperty()
    course_name = db.StringProperty()

class ClassForm(djangoforms.ModelForm):
    class Meta:
	model = Class

class StudentClass(db.Model):
    student = db.ReferenceProperty(Student)
    class_ = db.ReferenceProperty(Class)
    rating = db.StringProperty()
    comment = db.StringProperty()
    grade = db.StringProperty()

class Book(db.Model):
    isbn = db.StringProperty()
    title = db.StringProperty()
    author = db.StringProperty()

class StudentBook(db.Model):
    student = db.ReferenceProperty(Student)
    book = db.ReferenceProperty(Book)
    rating = db.StringProperty()
    comment = db.TextProperty()
        
class Paper(db.Model):
    paper_category = db.StringProperty(choices = ["journal", "conference"])
    title = db.StringProperty()
    author = db.StringProperty()

class StudentPaper(db.Model):
    student = db.ReferenceProperty(Student)
    paper = db.ReferenceProperty(Paper)
    rating = db.StringProperty()
    comment = db.TextProperty()

class Internship(db.Model):
    place_name = db.StringProperty()
    location = db.StringProperty()
    semester = db.StringProperty()

class StudentInternship(db.Model):
    student = db.ReferenceProperty(Student)
    internship = db.ReferenceProperty(Internship)
    rating = db.StringProperty()
    comment = db.TextProperty()

class Place(db.Model):
    place_type = db.StringProperty(choices = ["study_place", "live_place", "eat_place", "fun_place"])
    place_name = db.StringProperty()
    location = db.StringProperty()
    semester = db.StringProperty()

class StudentPlace(db.Model):
    student = db.ReferenceProperty(Student)
    place = db.ReferenceProperty(Place)
    rating = db.StringProperty()
    comment = db.TextProperty()

class Game(db.Model):
    os = db.StringProperty()
    title = db.StringProperty()

class StudentGame(db.Model):
    student = db.ReferenceProperty(Student)
    game = db.ReferenceProperty(Game)
    rating = db.StringProperty()
    comment = db.TextProperty()

def findAddBook(title, author='', isbn=''):
    """
    Find and return the given book, or create and add it to the database.
    Returns the book object.
    """
    # may use in phase 2
    #. though see get_or_insert - does something similar

    q = Book.all()
    q.filter("title = ", title)
    # q.filter("author = ", author)
    # q.filter("isbn = ", isbn)

    results = q.fetch(1)
    if results:
        book = results[0]
    else:
        book = Book()
        book.title = title
        book.author = author
        book.isbn = isbn
        book.put()

    return book
