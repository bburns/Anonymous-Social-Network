import string
import random
import re

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms







# validation functions
# can be used by passing it as a param in a Property  declaration
#       eg:   course_num = db.StringProperty(validator=validate_course_num)

# student validations
def validate_email(email):
    if not email:
	raise db.BadValueError
    regex = "[a-z0-9\-\.\_]+\@[a-z]+\.[a-z]+[\.[a-z]*]?"
    if re.match(regex, email) == None:
	raise db.BadValueError("Invalid value entered. eg: email@email.com")

# rating valiation
def validate_rating(val):
    if val:
	regex = "[0-9]*"
	if re.match(regex, str(val)) == None:
	    raise db.BadValueError("Invalid value entered. Rating must be an integer value")
	elif val < 0 :
	    raise db.BadValueError("Invalid value entered. Rating value cannot be negative")
	elif val > 100 :
	    raise db.BadValueError("Invalid value entered. Rating value cannot greater than 100")

# class validations
def validate_course_num(val):
    if not val:
	raise db.BadValueError("This field is required.")
    regex = "[A-Z]([A-Z]|\s){0,2}\s?[f|s|w|n]?[0-9]{3}[A-Z]{0,2}"
    if re.match(regex, val) == None:
        raise db.BadValueError("Invalid value entered. eg: CS 341, EE 316")

def validate_semester(semester):
    if semester :
	regex = "(Fall|Spring|Summer)\s?[0-9]{4}"
	if re.match(regex, semester) == None:
	   raise db.BadValueError("Invalid value entered. eg: Spring 2009, Fall 2002")

def validate_unique(unique):
    if unique :
	regex = "[0-9]{5}"
	if re.match(regex, unique) == None:
	   raise db.BadValueError("Invalid value entered. Please enter 5 digit numbers only")

def validate_grade(val):
    if val:
	regex = "(([B-D][+|\-]?)|A|A\-|F|P|CR|NC|Q|I|X)?"
	if re.match(regex, val) == None:
		raise db.BadValueError

# book validations

def validate_isbn(val):
    if val:
    	regex = "\S{8}"
   	if re.match(regex, val)== None:
		raise db.BadValueError("Invalid value entered. Please enter 10 or 13 digit numbers only")



class Student(db.Model):
    # this has to come before the User class, because it references Student. 
    
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

    def generateID(self):
        random.seed(8)
        d = [random.choice(string.letters + string.digits) for x in xrange(8)]
        self.id_ = "".join(d)


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
class Class(db.Model):
    course_num = db.StringProperty(validator=validate_course_num)
    course_name = db.StringProperty()
    unique = db.StringProperty(validator=validate_unique)
    semester = db.StringProperty(validator=validate_semester)
    instructor = db.StringProperty()
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

class StudentClass(db.Model):
    student = db.ReferenceProperty(Student)
    class_ = db.ReferenceProperty(Class)
    rating = db.StringProperty(validator=validate_rating)
    comment = db.StringProperty()
    grade = db.StringProperty(validator=validate_grade)


class Book(db.Model):
    title = db.StringProperty()
    author = db.StringProperty()
    isbn = db.StringProperty(validator=validate_isbn)

    # store aggregate info here, so don't have to do expensive joins
    # update in StudentBook.put method
    ratingAvg = db.IntegerProperty(validator=validate_rating) # 0 to 100
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
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()

    def put(self):
        db.Model.put(self) # call superclass
        
        # now update avg and count properties for book.
        book = self.book
        
        # get all the refs to this book - this is a list of assoc objects,
        # each with a rating and comment. 
        sbs = book.studentbook_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5?
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
    semester = db.StringProperty(validator=validate_semester)
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
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()

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
    rating = db.StringProperty(validator=validate_rating)
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
