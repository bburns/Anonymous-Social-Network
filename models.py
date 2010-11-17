"""
models.py
Defines all the appengine model classes, with validation functions,
and associated Django form classes. 
"""


import string
import random
import re
import logging

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms



# validation functions
# can be used by passing it as a param in a Property  declaration
#       eg:   course_num = db.StringProperty(validator=validate_course_num)

# student validations
# def validate_email(email):
    # if email: 
        # regex = "[a-z0-9\-\.\_]+\@[a-z]+\.[a-z]+[\.[a-z]*]?"
        # if re.match(regex, email) == None:
            # raise db.BadValueError("Invalid value entered. eg: email@email.com: "   + email)


# rating valiation
def validate_rating(val):
    if val:
        regex = "[0-9]+"
        if re.match(regex, str(val)) == None:
            raise db.BadValueError("Invalid value entered. Rating must be an integer value")
        elif int(val) < 0 :
            raise db.BadValueError("Invalid value entered. Rating value cannot be negative")
        elif int(val) > 100 :
            raise db.BadValueError("Invalid value entered. Rating value cannot greater than 100")

# class validations
   
def validate_course_num(val):
    if val :    
        regex = "[A-Z]([A-Z]|\s){0,3}\s?[f|s|w|n]?[0-9]{3}[A-Z]{0,2}$"
        if re.match(regex, val) == None:
            raise db.BadValueError("Invalid value entered. Should look like CS 341, or EE 316.")

def validate_semester(semester):
    if semester :
        regex = "(Fall|Spring|Summer)\s?[0-9]{4}$"
        if re.match(regex, semester) == None:
            raise db.BadValueError("Invalid value entered. Should look like Spring 2009, or Fall 2002.")
    
def validate_unique(unique):
    if unique :
        regex = "[0-9]{5}$"
        if re.match(regex, unique) == None:
            raise db.BadValueError("Invalid value entered. Please enter 5 digit numbers only.")

def validate_grade(val):
    if val:
        regex = "(([B-D][+|\-]?)|A|A\-|F|P|CR|NC|Q|I|X)$"
        if re.match(regex, val) == None:
            raise db.BadValueError

# book validations
def validate_isbn(val):
    if val:
        #regex = "\S{8}"
        regex = "[0-9]{10}$|[0-9]{13}$"
        if re.match(regex, val)== None:
            raise db.BadValueError("Invalid value entered. Please enter 10 or 13 digit numbers only.")

class Student(db.Model):
    
    id_ = db.StringProperty()   # id is reserved in python(?)
    password = db.StringProperty()
    isAdmin = db.BooleanProperty()
    lastLogin = db.StringProperty()
    dateTime = db.DateTimeProperty(auto_now=True)

    def setLastLogin(self, string) :
	      self.lastLogin = string

    @staticmethod
    def get_by_username(id_):
        q = db.Query(Student)
        q = q.filter('id_', id_)
        results = q.fetch(limit=1)
        if results:
           user = results[0]
        else:
           user = None
        return user

    def generateID(self):
        random.seed()
        d = [random.choice(string.letters + string.digits) for x in xrange(8)]
        self.id_ = "".join(d)

    def generatePassword(self):
        random.seed()
        d = [random.choice(string.letters + string.digits) for x in xrange(8)]
        self.password = "".join(d)


    def put(self):
        """
        Override this so we can set isAdmin flag
        """
        
        # set admin flag for us (leaving josh out for testing purposes)
        if self.id_ in ["brian000", "ben00000", "shanky00", "jonathan", "admin000"]:
            self.isAdmin = True
        
        # call superclass
        db.Model.put(self)

        

    # for phase 3?
    # def addBook(self, title, author='', isbn='', rating=None, comment=''):
        # """
        # Add the given book as a related object for this student. 
        # Creates the book if it can't find it in the database.
        # """
        # sb = StudentBook()
        # sb.student = self
        # sb.book = Book.findAdd(title, author, isbn)
        # sb.rating = rating
        # sb.comment = comment
        # sb.put()



class Class(db.Model):
    """
    Ideally this would be split into Course (cs 343 ai) and Class (unique#, semester, prof).
    Originally this had unique# and semester here, but moved those into the association class,
    so coursenum, coursename and instructor all get rated together.
    """

    # We could specify properties to be required here, but then you wouldn't be allowed
    # to create empty objects. So we override put instead, to catch missing properties. 
    
    course_num = db.StringProperty(validator=validate_course_num, verbose_name="Course Number")
    course_name = db.StringProperty()
    instructor = db.StringProperty()

    # store aggregate info here, so don't have to do expensive joins to get it.
    # updated in StudentClass.put method.
    ratingAvg = db.IntegerProperty() # 0 to 100
    gradeAvg = db.StringProperty()
    refCount = db.IntegerProperty()
    
    edit_time = db.DateTimeProperty(auto_now=True)
  
    def put(self):
        "Override this so we can catch required fields"
        if not self.course_num:
            raise db.BadValueError("Course number is a required field.")
        else:
            db.Model.put(self) # call the superclass

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Class).order("-edit_time")
        results = q.fetch(limit)
        return results

    @staticmethod
    def findAdd(course_num, course_name='', instructor=''):
        """
        Find and return the given class, or create and add it to the database.
        Does an exact match on coursenum, ignores coursename, and does
        a partial match on instructor (eg "Glen Downing" will match "Downing"). 
        Returns the class object.
        """
        q = Class.all()
        q.filter("course_num = ", course_num)
        #q.filter("course_name = ", course_name)
        #q.filter("instructor = ", instructor)
        #results = q.fetch(1)

        # can't do anything like this with GQL
        #q = Class.gql("WHERE course_num=:1 AND (instructor IN :2 OR :3 IN instructor)", course_num, instructor, instructor)
        #results = q.fetch(1)

        # iterate over all the classes with the same course number, 
        # check for ones that have the same (or similar instructor), add them
        # to a resultset. 
        # really should just get one match, but throw them all in a list anyway. 
        results = []
        for c in q:
            # this handles things like "Downing" matching "Glen Downing" or vice-versa
            if (c.instructor in instructor) or (instructor in c.instructor):
                results.append(c)

        if results:
            c = results[0]
        else:
            # no match found so create a new class object
            c = Class()
            c.course_num = course_num
            c.course_name = course_name
            c.instructor = instructor
            c.put()
        return c


class ClassForm(djangoforms.ModelForm):
    class Meta:
        model = Class
        exclude = ['ratingAvg', 'gradeAvg', 'refCount']



class Rating:
    """
    """
    # oh, gae already has a RatingProperty type.
    # see http://code.google.com/appengine/docs/python/datastore/typesandpropertyclasses.html#Rating

    # this would be nice for forms, but then we're importing all kinds of weird data, so 
    # using this in the property definition would throw errors on seeing that data. 
    # if we had control over the schema we could have limited ratings to these values or something. 
    choices = ['0','10','20','30','40','50','60','70','80','90','100']


class Grade:
    """
    Just a place to store code and dicts for now. 
    Could make into a gae property type. 
    Need to define this before StudentClass, as it references this class.
    A  	4.00
    A- 	3.70
    B+ 	3.30
    B   3.00
    B- 	2.70
    C+ 	2.30
    C 	2.00
    C- 	1.70
    D+ 	1.30
    D 	1.00
    D- 	0.70
    F 	0.00
    """

    # store maps here so don't need to keep parsing them
    mapNum = {'A':4.0, 'B':3.0, 'C':2.0, 'D':1.0, 'F':0.0}
    mapLetter = {0:'F',1:'F',2:'D-',3:'D',4:'D+',5:'C-',6:'C',7:'C+', \
                8:'B-',9:'B',10:'B+',11:'A-',12:'A'}
    mapAdjust = {'+':0.3, '-':-0.3, '':0.0}

    # don't include these grades in the average calculation
    skipGrades = set(['','P','CR','NC','Q','I','X'])

    # choices used in property definition (and hence dropdowns)
    choices = ['','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','P','CR','NC','Q','I','X']

    @staticmethod
    def gradeToNum(s):
        """
        Convert grade string to its numeric representation, eg 'A-' to 3.7. 
        """
        # preconditions
        assert (len(s)==1 or len(s)==2)
        
        letter = s[0]
        plusminus = s[1] if len(s)>1 else ''
        n = Grade.mapNum[letter]
        adjustment = Grade.mapAdjust[plusminus]
        n = n + adjustment
        
        # postconditions
        assert (n>=0 and n <=4)
        return n

    @staticmethod
    def numToGrade(x):
        """
        Convert grade point to its string representation, eg 3.9 to 'A'.
        If A- is 3.7, and A is 4.0, the cutoff should be halfway between them, at 3.85.
        Ie a 3.85 would be rounded up to an A. 
        I played around with the scale in Excel and came up with an approximately
        linear conversion process. It'll do. 
        """
        # preconditions
        assert (x>=0 and x <=4)
        
        i = int(x * 3.1)
        s = Grade.mapLetter[i]
        
        # postconditions
        assert (len(s)==1 or len(s)==2)
        return s

    @staticmethod
    def getAvgGrade(grades):
        """
        Get average of a list of grades, as a letter grade, eg 'B'.
        Grades can be empty strings, or Q's, etc, and will be ignored. 
        If list has no grades, will return an empty string. 
        eg ['A','C',''] -> 'B'
        eg ['Q',''] -> ''
        eg [] -> ''
        """
        
        # remove invalid grades (blanks, Q's, etc)
        grades = [grade for grade in grades if grade not in Grade.skipGrades]
        logging.info(grades)
        
        # convert them to numbers, eg B to 3.0
        grades = map(Grade.gradeToNum, grades)
        logging.info(grades)

        # get the average
        ngrades = len(grades)
        avg = None if ngrades==0 else sum(grades) / ngrades
        
        # convert it to a string, eg 3.3 to B+
        # if it's None, return an empty string
        s = Grade.numToGrade(avg) if avg != None else ''
        logging.info(s)
        return s


class StudentClass(db.Model):
    student = db.ReferenceProperty(Student)
    class_ = db.ReferenceProperty(Class)
    semester = db.StringProperty(validator=validate_semester)
    unique = db.StringProperty(validator=validate_unique)
    grade = db.StringProperty(validator=validate_grade, choices=Grade.choices)
    #rating = db.StringProperty(validator=validate_rating, choices=Rating.choices) # bad mojo
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()
    #ratedThis = db.BooleanProperty()

    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        Also catch required fields here, for form validation.
        """
        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        #if not self.unique :
        #   raise db.BadValueError("Unique is a required field.")
        #if not self.semester :
        #   raise db.BadValueError("Semester is a required field.")
        if self.rating :
            ratedThis = True
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this class - links is a list of assoc objects, 
        # each with a rating and comment and grade. 
        c = self.class_
        links = c.studentclass_set
        logging.info(links)
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(link.rating) for link in links]
        nratings = len(ratings)
        ratingAvg = sum(ratings) / nratings
        logging.info(ratings)
        logging.info(ratingAvg)
        
        # get average grade
        # grade is optional, so may be empty string!
        grades = [link.grade for link in links]
        gradeAvg = Grade.getAvgGrade(grades)
        
        # update the class
        c.ratingAvg = ratingAvg
        c.gradeAvg = gradeAvg
        c.refCount = nratings
        c.put()
        logging.info('put')





class StudentClassForm(djangoforms.ModelForm):
    class Meta:
        model = StudentClass
        exclude = ['student','class_']

#    def is_valid(self):
        #. check for required properties here also



class Book(db.Model):
    title = db.StringProperty()
    author = db.StringProperty()
    isbn = db.StringProperty(validator=validate_isbn)
    ratingAvg = db.IntegerProperty(validator=validate_rating) # 0 to 100
    refCount = db.IntegerProperty()    
    edit_time = db.DateTimeProperty(auto_now=True)

    # def put(self) :
    #     "Override this so we can catch required fields"
    #     if not self.isbn:
    #         raise db.BadValueError("ISBN is a required field.")
    #     else:
    #         db.Model.put(self) # call the superclass

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Book).order("-edit_time")
        results = q.fetch(limit)
        return results
    
    @staticmethod
    def findAdd(title, author='', isbn=''):
        """
        Find and return the given book, or create and add it to the database.
        Returns the book object.
        """
        # get_or_insert does something similar in gae, but expects a key also. 
        # http://code.google.com/appengine/docs/python/datastore/modelclass.html#Model_get_or_insert

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
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        Also catch required fields here, for form validation.
        """

        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this book - links is a list of assoc objects, 
        # each with a rating and comment. 
        book = self.book
        links = book.studentbook_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(link.rating) for link in links]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        book.ratingAvg = ratingAvg
        book.refCount = n
        book.put()




class StudentBookForm(djangoforms.ModelForm):
    class Meta:
        model = StudentBook
        exclude = ['student','book']



class Paper(db.Model):
    #. add more choices, journal name, year, etc
    paper_category = db.StringProperty(choices = ["journal", "conference"])
    title = db.StringProperty()
    author = db.StringProperty()
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    edit_time = db.DateTimeProperty(auto_now=True)
    

    def put(self) :
        "Override this so we can catch required fields"
        if not self.paper_category:
            raise db.BadValueError("Paper category not selected.")
        else:
            db.Model.put(self) # call the superclass

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Paper).order("-edit_time")
        results = q.fetch(limit)
        return results

    @staticmethod
    def findAdd(title, author='', paper_category=''):
        """
        Find and return the given paper, or create and add it to the database.
        Does an exact match on title, ignores the rest.
        Returns the paper object.
        """
        q = Paper.all()
        q.filter("title = ", title)
        results = q.fetch(1)

        if results:
            o = results[0]
        else:
            # no match found so create a new paper object
            o = Paper()
            o.paper_category = paper_category
            o.title = title
            o.author = author
            o.put()
        return o



class PaperForm(djangoforms.ModelForm):
    class Meta:
        model = Paper
        exclude = ['ratingAvg', 'refCount']


class StudentPaper(db.Model):
    student = db.ReferenceProperty(Student)
    paper = db.ReferenceProperty(Paper)
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()


    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        Also catch required fields here, for form validation.
        """

        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this paper - links is a list of assoc objects, 
        # each with a rating and comment. 
        paper = self.paper
        links = paper.studentpaper_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(link.rating) for link in links]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        paper.ratingAvg = ratingAvg
        paper.refCount = n
        paper.put()


class StudentPaperForm(djangoforms.ModelForm):
    class Meta:
        model = StudentPaper
        exclude = ['student','paper']



class Internship(db.Model):
    place_name = db.StringProperty()
    location = db.StringProperty()
    semester = db.StringProperty(validator=validate_semester)
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    edit_time = db.DateTimeProperty(auto_now=True)
    
    # def put(self) :
    #     "Override this so we can catch required fields"
    #     if not self.semester:
    #         raise db.BadValueError("Semester is a required field.")
    #     else:
    #         db.Model.put(self) # call the superclass

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Internship).order("-edit_time")
        results = q.fetch(limit)
        return results

    @staticmethod
    def findAdd(place_name, location='', semester=''):
        """
        Find and return the given internship, or create and add it to the database.
        Does an exact match on place_name, ignores the rest.
        Returns the internship object.
        """
        q = Internship.all()
        q.filter("place_name = ", place_name)
        results = q.fetch(1)

        if results:
            o = results[0]
        else:
            # no match found so create a new internship object
            o = Internship()
            o.place_name = place_name
            o.location = location
            o.semester = semester
            o.put()
        return o



class InternshipForm(djangoforms.ModelForm):
    class Meta:
        model = Internship
        exclude = ['ratingAvg', 'refCount']

class StudentInternship(db.Model):
    student = db.ReferenceProperty(Student)
    internship = db.ReferenceProperty(Internship)
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()

    def put(self):
        """
        Also catch required fields here, for form validation.
        """
        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        
        db.Model.put(self) # call superclass
        internship = self.internship
        links = internship.studentinternship_set
        ratings = [int(link.rating) for link in links]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        internship.ratingAvg = ratingAvg
        internship.refCount = n
        internship.put()

class StudentInternshipForm(djangoforms.ModelForm):
    class Meta:
        model = StudentInternship
        exclude = ['student','internship']




class Place(db.Model):
    place_type = db.StringProperty(choices = ["study_place", "live_place", "eat_place", "fun_place"])
    place_name = db.StringProperty()
    location = db.StringProperty()
    semester = db.StringProperty(validator=validate_semester)
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    edit_time = db.DateTimeProperty(auto_now=True)

    def put(self) :
        "Override this so we can catch required fields"
        if not self.place_type:
            raise db.BadValueError("Place category not selected.")
        #if not self.semester:
        #    raise db.BadValueError("Semester is a required field.")
        else:
            db.Model.put(self) # call the superclass
    
    def get_pretty_place_name(self):
        if self.place_type ==  "eat_place":
            return "Restaurant"
        elif self.place_type == "live_place":
            return "Residence"
        elif self.place_type == "study_place":
            return "Study Area"
        else:
            return "Recreational Place"

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Place).order("-edit_time")
        results = q.fetch(limit)
        return results

    @staticmethod
    def findAdd(place_type, place_name, location='', semester=''):
        """
        Find and return the given item, or create and add it to the database.
        Does an exact match on place_type and place_name, ignores the rest.
        Returns the object.
        """
        q = Place.all()
        q.filter("place_type = ", place_type)
        q.filter("place_name = ", place_name)
        results = q.fetch(1)

        if results:
            o = results[0]
        else:
            # no match found so create a new object
            o = Place()
            o.place_type = place_type
            o.place_name = place_name
            o.location = location
            o.semester = semester
            o.put()
        return o




class PlaceForm(djangoforms.ModelForm):
    class Meta:
        model = Place
        exclude = ['ratingAvg', 'refCount']


class StudentPlace(db.Model):
    student = db.ReferenceProperty(Student)
    place = db.ReferenceProperty(Place)
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()
    
    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        Also catch required fields here, for form validation.
        """

        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this item - links is a list of assoc objects, 
        # each with a rating and comment. 
        place = self.place
        links = place.studentplace_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(link.rating) for link in links]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        place.ratingAvg = ratingAvg
        place.refCount = n
        place.put()


class StudentPlaceForm(djangoforms.ModelForm):
    class Meta:
        model = StudentPlace
        exclude = ['student','place']



class Game(db.Model):
    os = db.StringProperty()
    title = db.StringProperty()
    ratingAvg = db.IntegerProperty() # 0 to 100
    refCount = db.IntegerProperty()
    edit_time = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_by_date(limit = 5):
        q = db.Query(Game).order("-edit_time")
        results = q.fetch(limit)
        return results

    @staticmethod
    def findAdd(title, os=''):
        """
        Find and return the given item, or create and add it to the database.
        Does an exact match on title, ignores the rest.
        Returns the object.
        """
        q = Game.all()
        q.filter("title = ", title)
        results = q.fetch(1)

        if results:
            o = results[0]
        else:
            # no match found so create a new object
            o = Game()
            o.title = title
            o.os = os
            o.put()
        return o


class GameForm(djangoforms.ModelForm):
    class Meta:
        model = Game
        exclude = ['ratingAvg', 'refCount']

class StudentGame(db.Model):
    student = db.ReferenceProperty(Student)
    game = db.ReferenceProperty(Game)
    rating = db.StringProperty(validator=validate_rating)
    comment = db.TextProperty()
    
    def put(self):
        """
        Override the put method so can update the average rating and reference count
        properties for the rated item. 
        This will get called automatically on importing the xml, 
        when user rates an existing item, and when they add and rate a new item. 
        Also catch required fields here, for form validation.
        """

        if not self.rating:
            raise db.BadValueError("Rating is a required field.")
        
        # call superclass
        db.Model.put(self) 
        
        # get all the refs to this item - links is a list of assoc objects, 
        # each with a rating and comment. 
        game = self.game
        links = game.studentgame_set
        
        # get a list of rating values, and the average
        #. get rid of int when convert from string
        #. also could do scaling here - eg convert to 0-5? 
        # but maybe clearer to keep it consistent with the rest of the model - let the ui scale it.
        ratings = [int(link.rating) for link in links]
        n = len(ratings)
        ratingAvg = sum(ratings) / n
        
        # update the book
        game.ratingAvg = ratingAvg
        game.refCount = n
        game.put()


class StudentGameForm(djangoforms.ModelForm):
    class Meta:
        model = StudentGame
        exclude = ['student','game']

