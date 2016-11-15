"""
xmlImport
Import data from an xml file or string.
"""

from xml.dom import minidom
import logging

from models import *



def xmlImportFile(xmlfile):
    """
    Imports an xml file to a google database
    Input: A path to a relative file location as a string
    Output: True if imported entire file. 
    """
    logging.info("xmlImportFile")
    #. check file is valid
    dom = minidom.parse(xmlfile)
    return xmlImport(dom)


def xmlImportString(s):
    """
    Imports an xml string to a google database
    Input: A path to a relative file location as a string
    Output: True if imported entire file.
    """
    logging.info("xmlImportString")
    logging.info(type(s))
    # minidom may throw an exception if input is invalid, eg empty string,
    # or bad unicode characters (weird)
    try:
        dom = minidom.parseString(s)
    except Exception, e:
        print type(e)     # the exception instance
        print e.args      # arguments stored in .args
        print e           # __str__ allows args to printed directly

    return xmlImport(dom)



def xmlImport(dom):
    """
    Imports a dom (document object model) to a google database.
    Input: a dom, obtained by parsing an xml file, for instance. 
    Output: True if imported the whole dom, None otherwise (seems to fail silently)
    """

    logging.info("xmlImport")
    
    # the root node should be a 'students' element
    rootNode = dom.firstChild

    # iterate over all student nodes
    #for studentNode in rootNode.getElementsByTagName('student'): # this worked but it's slower
    for studentNode in rootNode.childNodes:
        # assert this true? NO - could be an empty element (due to CR's in text!)
        #assert (studentNode.nodeName == "student")
        if studentNode.nodeName == "student":

            # add the student to the database
            # will set isAdmin flag if id is recognized - see Student.put()
            s = Student()
            s.id_ = getElementData(studentNode, "id")
            s.password = getElementData(studentNode, "password")
            s.put()           
            logging.info(s.id_ + ' ' + s.password)

            # now look for child elements and add them also

            # class tag handler
            for node in studentNode.getElementsByTagName('class'):

                # get data from xml
                unique = getElementData(node, 'unique')
                course_num = getElementData(node, 'course_num')
                course_name = getElementData(node, 'course_name')
                semester = getElementData(node, 'semester')
                instructor = getElementData(node, 'instructor')
                grade = getElementData(node, 'grade')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                # find or add a class object
                o = Class.findAdd(course_num, course_name, instructor)
                logging.info(course_num)

                # create a studentClass association object
                link = StudentClass()
                link.student = s
                link.class_ = o
                link.unique = unique
                link.semester = semester
                link.grade = grade
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # books
            for node in studentNode.getElementsByTagName('book'):

                # get data from xml
                isbn = getElementData(node, 'isbn')
                author = getElementData(node, 'author')
                title = getElementData(node, 'title')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                # find or add a book object
                o = Book.findAdd(title, author, isbn)
                logging.info(title)

                # create a studentBook association object
                link = StudentBook()
                link.student = s
                link.book = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # papers
            for node in studentNode.getElementsByTagName('paper'):                

                # get data from xml
                paper_category = getElementData(node, 'paper_category')
                author = getElementData(node, 'author')
                title = getElementData(node, 'title')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                # find or add a paper object
                o = Paper.findAdd(title, author, paper_category)
                logging.info(title)

                # create association object
                link = StudentPaper()
                link.student = s
                link.paper = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # internship
            for node in studentNode.getElementsByTagName('internship'):           

                place_name = getElementData(node, 'place_name')             
                location = getElementData(node, 'location')
                semester = getElementData(node, 'semester')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Internship.findAdd(place_name, location, semester)
                logging.info(place_name)

                link = StudentInternship()
                link.student = s
                link.internship = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # studyPlace
            for node in studentNode.getElementsByTagName('study_place'):          

                place_type = "study_place"
                place_name = getElementData(node, 'place_name')
                location = getElementData(node, 'location')
                semester = getElementData(node, 'semester')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Place.findAdd(place_type, place_name, location, semester)
                logging.info(place_name)

                link = StudentPlace()
                link.student = s
                link.place = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # livePlace
            for node in studentNode.getElementsByTagName('live_place'):           

                place_type = "live_place"
                place_name = getElementData(node, 'place_name')
                location = getElementData(node, 'location')
                semester = getElementData(node, 'semester')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Place.findAdd(place_type, place_name, location, semester)
                logging.info(place_name)

                link = StudentPlace()
                link.student = s
                link.place = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # eatPlace
            for node in studentNode.getElementsByTagName('eat_place'):            

                place_type = "eat_place"
                place_name = getElementData(node, 'place_name')
                location = getElementData(node, 'location')
                semester = getElementData(node, 'semester')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Place.findAdd(place_type, place_name, location, semester)
                logging.info(place_name)

                link = StudentPlace()
                link.student = s
                link.place = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # funPlace
            for node in studentNode.getElementsByTagName('fun_place'):            

                place_type = "fun_place"
                place_name = getElementData(node, 'place_name')
                location = getElementData(node, 'location')
                semester = getElementData(node, 'semester')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Place.findAdd(place_type, place_name, location, semester)
                logging.info(place_name)

                link = StudentPlace()
                link.student = s
                link.place = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

            # game
            for node in studentNode.getElementsByTagName('game'):                 

                os = getElementData(node, 'os')
                title = getElementData(node, 'title')
                rating = getElementData(node, 'rating')
                comment = getElementData(node, 'comment')

                o = Game.findAdd(title, os)
                logging.info(title)

                link = StudentGame()
                link.student = s
                link.game = o
                link.rating = rating
                link.comment = comment
                link.put()
                logging.info("added link")

    return True
    

def getElementData(node, tagname) :
    """
    Get the data from a child element of the given node.
    If the element specified by tagname doesn't exist, returns "". 
    Input: minidom node, tagname to look for
    Output: An empty string or the data.
    """
    
    nodes = node.getElementsByTagName(tagname)
    if nodes:
        e = nodes[0].firstChild
        if e is None:
            return ""
        else:
            return e.data
    else:
        return ""

