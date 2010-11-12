"""
xmlImport
Import data from an xml file or string.
"""

from xml.dom import minidom
from models import *


def xmlImportFile(xmlfile):
    """
    Imports an xml file to a google database
    Input: A path to a relative file location as a string
    Output: None. but there is a database created that you can now query.
    """
    #. check file is valid
    dom = minidom.parse(xmlfile)
    return xmlImport(dom)


def xmlImportString(s):
    """
    Imports an xml string to a google database
    Input: A path to a relative file location as a string
    Output: None. but there is a database created that you can now query.    
    """
    # minidom may throw an exception if input is invalid, eg empty string
    dom = minidom.parseString(s)
    return xmlImport(dom)



def xmlImport(dom):
    """
    Imports a dom (document object model) to a google database.
    Input: a dom, obtained by parsing an xml file, for instance. 
    Output: None. but there is a database created that you can now query.    
    """

    # the root node should be a 'students' element
    rootNode = dom.firstChild

    # iterate over all student nodes
    #for studentNode in rootNode.getElementsByTagName('student'): # this worked but it's slower
    for studentNode in rootNode.childNodes:
        # assert this true? NO - could be an empty element (due to CR's in text!)
        #assert (studentNode.nodeName == "student")
        if studentNode.nodeName == "student":

            # add the student to the database
            s = Student()
            s.id_ = getElementData(studentNode, "id")
            s.password = getElementData(studentNode, "password")
            s.put()

            # now look for child elements and add them also

            # class tag handler
            for node in studentNode.getElementsByTagName('class'):

                # find or add a class object
                unique = getElementData(node, 'unique')
                course_num = getElementData(node, 'course_num')
                course_name = getElementData(node, 'course_name')
                semester = getElementData(node, 'semester')
                instructor = getElementData(node, 'instructor')
                c = Class.findAdd(course_num, course_name, instructor)

                #create a studentClass association class
                sc = StudentClass()
                sc.student = s
                sc.class_ = c
                sc.unique = unique
                sc.semester = semester
                sc.grade = getElementData(node, 'grade')
                sc.rating = getElementData(node, 'rating')
                sc.comment = getElementData(node, 'comment')
                sc.put()                    

            # books
            for node in studentNode.getElementsByTagName('book'):

                # find or add a book object
                isbn = getElementData(node, 'isbn')
                author = getElementData(node, 'author')
                title = getElementData(node, 'title')
                b = Book.findAdd(title, author, isbn)

                # create a studentBook association class
                sb = StudentBook()
                sb.student = s
                sb.book = b
                sb.rating = getElementData(node, 'rating')
                sb.comment = getElementData(node, 'comment')
                sb.put()    

            # papers
            for node in studentNode.getElementsByTagName('paper'):                

                p = Paper()
                p.paper_category = getElementData(node, 'paper_category')
                p.author = getElementData(node, 'author')
                p.title = getElementData(node, 'title')
                p.put()

                sp = StudentPaper()
                sp.student = s
                sp.paper = p
                sp.rating = getElementData(node, 'rating')
                sp.comment = getElementData(node, 'comment')
                sp.put()

            # internship
            for node in studentNode.getElementsByTagName('internship'):           

                i = Internship()
                i.place_name = getElementData(node, 'place_name')             
                i.location = getElementData(node, 'location')
                i.semester = getElementData(node, 'semester')
                i.put()

                si = StudentInternship()
                si.student = s
                si.internship = i
                si.rating = getElementData(node, 'rating')
                si.comment = getElementData(node, 'comment')

                si.put()

            # studyPlace
            for node in studentNode.getElementsByTagName('study_place'):          

                sp = Place()
                sp.place_type = "study_place"
                sp.place_name = getElementData(node, 'place_name')
                sp.location = getElementData(node, 'location')
                sp.semester = getElementData(node, 'semester')
                sp.put()

                ssp = StudentPlace()
                ssp.student = s
                ssp.place = sp
                ssp.rating = getElementData(node, 'rating')
                ssp.comment = getElementData(node, 'comment')
                ssp.put()

            # livePlace
            for node in studentNode.getElementsByTagName('live_place'):           

                lp = Place()
                lp.place_type = "live_place"
                lp.place_name = getElementData(node, 'place_name')
                lp.location = getElementData(node, 'location')
                lp.semester = getElementData(node, 'semester')
                lp.put()

                slp = StudentPlace()
                slp.student = s
                slp.place = lp
                slp.rating = getElementData(node, 'rating')
                slp.comment = getElementData(node, 'comment')
                slp.put()

            # eatPlace
            for node in studentNode.getElementsByTagName('eat_place'):            

                ep = Place()
                ep.place_type = "eat_place"
                ep.place_name = getElementData(node, 'place_name')
                ep.location = getElementData(node, 'location')
                ep.semester = getElementData(node, 'semester')
                ep.put()

                sep = StudentPlace()
                sep.student = s
                sep.place = ep
                sep.rating = getElementData(node, 'rating')
                sep.comment = getElementData(node, 'comment')
                sep.put()

            # funPlace
            for node in studentNode.getElementsByTagName('fun_place'):            

                fp = Place()
                fp.place_type = "fun_place"
                fp.place_name = getElementData(node, 'place_name')
                fp.location = getElementData(node, 'location')
                fp.semester = getElementData(node, 'semester')
                fp.put()

                sfp = StudentPlace()
                sfp.student = s
                sfp.place = fp
                sfp.rating = getElementData(node, 'rating')
                sfp.comment = getElementData(node, 'comment')
                sfp.put()

            # game
            for node in studentNode.getElementsByTagName('game'):                 

                g = Game()
                g.os = getElementData(node, 'os')
                g.title = getElementData(node, 'title')
                g.put()

                sg = StudentGame()
                sg.student = s
                sg.game = g
                sg.rating = getElementData(node, 'rating')
                sg.comment = getElementData(node, 'comment')
                sg.put()
            

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

