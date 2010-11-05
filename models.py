"""
models.py
Defines all the appengine model classes, with validation functions,
and associated Django form classes. 
"""


import string
import random
import re

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms





# validation functions
# can be used by passing it as a param in a Property  declaration
#       eg:   course_num = db.StringProperty(validator=validate_course_num)
def validate_email(email):
    if not email:
	raise db.BadValueError
    regex = "[a-z0-9\-\.\_]+\@[a-z]+\.[a-z]+[\.[a-z]*]?"
    if re.match(regex, email) == None:
	raise db.BadValueError("Invalid value entered. eg: email@email.com")

def validate_course_num(val):
    # if not val:
	# raise db.BadValueError("This field is required.")
    # regex = "[A-Z]([A-Z]|\s){0,2}\s?[f|s|w|n]?[0-9]{3}[A-Z]{0,2}"
    # if re.match(regex, val) == None:
        # raise db.BadValueError("Invalid value entered. eg: CS 345, CS 313K ")
    pass
    

def validate_semester(semester):
    # if semester :
	# regex = "(Fall|Spring|Summer)\s?[0-9]{4}"
	# if re.match(regex, semester) == None:
        # print semester
	   # raise db.BadValueError("Invalid value entered. eg: Spring 2009, Fall 2002")
    pass
    
def validate_unique(unique):
    # if unique :
	# regex = "[0-9]{5}"
	# if re.match(regex, unique) == None:
	   # raise db.BadValueError("Invalid value entered. Please enter 5 digit numbers only")
    pass
    




def validate_grade(val):
    if not val:
	raise db.BadValueError
    regex = "(([B-D][+|\-]?)|A|A\-|F|P|CR|NC|Q|I|X)?"
    if re.match(regex, val) == None:
	raise db.BadValueError

def validate_isbn(val):
    if not val:
	raise db.BadValueError
    regex = "\S{8}"
    if re.match(regex, val)== None:
	raise db.BadValueError

def validate_rating(val):
    # if val:
	if val < 0 :
	    raise db.BadValueError
	if val > 100 :
	    raise db.BadValueError



class Student(db.Model):
    # this has to come before the User class, because it references Student. 
    
    id_ = db.StringProperty()   # id is reserved in python
    password = db.StringProperty()

    def generateID(self):
        random.seed(8)
        d = [random.choice(string.letters + string.digits) for x in xrange(8)]
        self.id_ = "".join(d)

    # for phase 3?
    # def addBook(self, title, author='', isbn='', rating=None, comment=''):
        # """
        # Add the given book as a related object for this student. 
        # Creates the book if it can't find it in the database.
        # """
        # sb = StudentBook()
        # sb.student = self
        # sb.book = findAddBook(title, author, isbn)
        # sb.rating = rating
        # sb.comment = comment
        # sb.put()


class User(db.Model):
    email = db.EmailProperty(validator=validate_email)
    password = db.StringProperty()
    isAdmin = db.BooleanProperty()
    student = db.ReferenceProperty(Student)

    @staticmethod
    def get_by_email(email):
        q = db.Query(User)
        q = q.filter('email', email)
        results = q.fetch(limit=1)
        #logging.info(results)
        if results:
            user = results[0]
        else:
            user = None
        return user

    def authenticate(self):
        pass


class UserForm(djangoforms.ModelForm):
    class Meta:
        model = User
        exclude = ['isAdmin','student']

		

#. ideally this would be split into Course (cs 343 ai) and Class (unique#, semester, prof)
#. or maybe just put semester and unique into the association class,
# so coursenum,name and instructor all get rated together
class Class(db.Model):
    course_num = db.StringProperty(validator=validate_course_num)
    course_name = db.StringProperty()
    unique = db.StringProperty(validator=validate_unique)
    semester = db.StringProperty(validator=validate_semester)
    instructor = db.StringProperty()

    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()

    edit_time = db.DateTimeProperty(auto_now=True)
  
    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Class)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]

class ClassForm(djangoforms.ModelForm):
    class Meta:
        model = Class
	exclude = ['ratingAvg', 'refCount']

class StudentClass(db.Model):
    student = db.ReferenceProperty(Student)
    class_ = db.ReferenceProperty(Class)
    rating = db.StringProperty()
    comment = db.StringProperty()
    grade = db.StringProperty()

    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        """
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this class - scs is a list of assoc objects, 
        # each with a raating and comment. 
	class_ = self.class_
	scs = class_.studentclass_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(sc.rating) for sc in scs]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the class
        class_.ratingAvg = ratingAvg
        class_.refCount = n
        class_.put()


class Book(db.Model):
    title = db.StringProperty()
    author = db.StringProperty()
    isbn = db.StringProperty()

    # store aggregate info here, so don't have to do expensive joins to get it.
    # values are updated in StudentBook.put method.
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    
    edit_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Book)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]


class BookForm(djangoforms.ModelForm):
    class Meta:
        model = Book
        exclude = ['ratingAvg', 'refCount']

class StudentBook(db.Model):
    student = db.ReferenceProperty(Student)
    book = db.ReferenceProperty(Book)
    rating = db.StringProperty()
    comment = db.TextProperty()

    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        """
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this book - sbs is a list of assoc objects, 
        # each with a rating and comment. 
        book = self.book
        sbs = book.studentbook_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(sb.rating) for sb in sbs]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        book.ratingAvg = ratingAvg
        book.refCount = n
        book.put()


#. add more choices, journal name, year, etc
class Paper(db.Model):
    paper_category = db.StringProperty(choices = ["journal", "conference"])
    title = db.StringProperty()
    author = db.StringProperty()
    edit_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Paper)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]

class PaperForm(djangoforms.ModelForm):
    class Meta:
        model = Paper

class StudentPaper(db.Model):
    student = db.ReferenceProperty(Student)
    paper = db.ReferenceProperty(Paper)
    rating = db.StringProperty()
    comment = db.TextProperty()

class Internship(db.Model):
    place_name = db.StringProperty()
    location = db.StringProperty()
    semester = db.StringProperty()
    edit_time = db.DateTimeProperty(auto_now=True)
    
    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Internship)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]

class InternshipForm(djangoforms.ModelForm):
    class Meta:
        model = Internship

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
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    edit_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Place)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]

class PlaceForm(djangoforms.ModelForm):
    class Meta:
        model = Place


class StudentPlace(db.Model):
    student = db.ReferenceProperty(Student)
    place = db.ReferenceProperty(Place)
    rating = db.StringProperty()
    comment = db.TextProperty()
    
    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        """
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this book - sbs is a list of assoc objects, 
        # each with a rating and comment. 
        place = self.place
        sps = place.studentplace_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(sp.rating) for sp in sps]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        place.ratingAvg = ratingAvg
        place.refCount = n
        place.put()


class Game(db.Model):
    os = db.StringProperty()
    title = db.StringProperty()
    edit_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_by_date(limit = 5):
    	q = db.Query(Game)
    	results = q.fetch(837548)
    	results = sorted(results, key=lambda time: time.edit_time, reverse = True)
    	return results[0:5]

class GameForm(djangoforms.ModelForm):
    class Meta:
        model = Game

class StudentGame(db.Model):
    student = db.ReferenceProperty(Student)
    game = db.ReferenceProperty(Game)
    rating = db.StringProperty()
    comment = db.TextProperty()



# def findAddBook(title, author='', isbn=''):
    # """
    # Find and return the given book, or create and add it to the database.
    # Returns the book object.
    # """
    # # may use in phase 3?
    # # . though see get_or_insert - does something similar

    # q = Book.all()
    # q.filter("title = ", title)
    # # q.filter("author = ", author)
    # # q.filter("isbn = ", isbn)

    # results = q.fetch(1)
    # if results:
        # book = results[0]
    # else:
        # book = Book()
        # book.title = title
        # book.author = author
        # book.isbn = isbn
        # book.put()

    # return book
