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
    Output: None. but there is a database created that you can now query.
    """
    logging.info("xmlImportFile")
    #. check file is valid
    dom = minidom.parse(xmlfile)
    return xmlImport(dom)


def xmlImportString(s):
    """
    Imports an xml string to a google database
    Input: A path to a relative file location as a string
    Output: None. but there is a database created that you can now query.    
    """
    logging.info("xmlImportString")
    logging.info(type(s))
    # minidom may throw an exception if input is invalid, eg empty string
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
    Output: None. but there is a database created that you can now query.    
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
            s = Student()
            s.id_ = getElementData(studentNode, "id")
            s.password = getElementData(studentNode, "password")
            s.put()
            
            logging.info(s.id_ + ' ' + s.password)

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
                logging.info(c.course_num)

                #create a studentClass association class
                sc = StudentClass()
                sc.student = s
                sc.class_ = c
                sc.unique = unique
                sc.semester = semester
                sc.grade = getElementData(node, 'grade')
                sc.rating = getElementData(node, 'rating')
                sc.comment = getElementData(node, 'comment')
                logging.info(sc.grade)
                logging.info(sc.rating)
                logging.info(sc.comment)
                sc.put()
                logging.info("added link")

            # books
            for node in studentNode.getElementsByTagName('book'):

                # find or add a book object
                isbn = getElementData(node, 'isbn')
                author = getElementData(node, 'author')
                title = getElementData(node, 'title')
                b = Book.findAdd(title, author, isbn)
                logging.info(b.title)

                # create a studentBook association class
                sb = StudentBook()
                logging.info("got sb")
                sb.student = s
                sb.book = b
                sb.rating = getElementData(node, 'rating')
                logging.info(sb.rating)
                sb.comment = getElementData(node, 'comment')
                logging.info(sb.comment)
                sb.put()
                logging.info("added link")

            # papers
            for node in studentNode.getElementsByTagName('paper'):                

                p = Paper()
                p.paper_category = getElementData(node, 'paper_category')
                p.author = getElementData(node, 'author')
                p.title = getElementData(node, 'title')
                p.put()
                logging.info(p.title)

                sp = StudentPaper()
                sp.student = s
                sp.paper = p
                sp.rating = getElementData(node, 'rating')
                sp.comment = getElementData(node, 'comment')
                sp.put()
                logging.info("added link")

            # internship
            for node in studentNode.getElementsByTagName('internship'):           

                i = Internship()
                i.place_name = getElementData(node, 'place_name')             
                i.location = getElementData(node, 'location')
                i.semester = getElementData(node, 'semester')
                i.put()
                logging.info(i.location)

                si = StudentInternship()
                si.student = s
                si.internship = i
                si.rating = getElementData(node, 'rating')
                si.comment = getElementData(node, 'comment')
                si.put()
                logging.info("added link")

            # studyPlace
            for node in studentNode.getElementsByTagName('study_place'):          

                sp = Place()
                sp.place_type = "study_place"
                sp.place_name = getElementData(node, 'place_name')
                sp.location = getElementData(node, 'location')
                sp.semester = getElementData(node, 'semester')
                sp.put()
                logging.info(sp.place_name)

                ssp = StudentPlace()
                ssp.student = s
                ssp.place = sp
                ssp.rating = getElementData(node, 'rating')
                ssp.comment = getElementData(node, 'comment')
                ssp.put()
                logging.info("added link")

            # livePlace
            for node in studentNode.getElementsByTagName('live_place'):           

                lp = Place()
                lp.place_type = "live_place"
                lp.place_name = getElementData(node, 'place_name')
                lp.location = getElementData(node, 'location')
                lp.semester = getElementData(node, 'semester')
                lp.put()
                logging.info(lp.place_name)

                slp = StudentPlace()
                slp.student = s
                slp.place = lp
                slp.rating = getElementData(node, 'rating')
                slp.comment = getElementData(node, 'comment')
                slp.put()
                logging.info("added link")

            # eatPlace
            for node in studentNode.getElementsByTagName('eat_place'):            

                ep = Place()
                ep.place_type = "eat_place"
                ep.place_name = getElementData(node, 'place_name')
                ep.location = getElementData(node, 'location')
                ep.semester = getElementData(node, 'semester')
                ep.put()
                logging.info(ep.place_name)

                sep = StudentPlace()
                sep.student = s
                sep.place = ep
                sep.rating = getElementData(node, 'rating')
                sep.comment = getElementData(node, 'comment')
                sep.put()
                logging.info("added link")

            # funPlace
            for node in studentNode.getElementsByTagName('fun_place'):            

                fp = Place()
                fp.place_type = "fun_place"
                fp.place_name = getElementData(node, 'place_name')
                fp.location = getElementData(node, 'location')
                fp.semester = getElementData(node, 'semester')
                fp.put()
                logging.info(fp.place_name)

                sfp = StudentPlace()
                sfp.student = s
                sfp.place = fp
                sfp.rating = getElementData(node, 'rating')
                sfp.comment = getElementData(node, 'comment')
                sfp.put()
                logging.info("added link")

            # game
            for node in studentNode.getElementsByTagName('game'):                 

                g = Game()
                g.os = getElementData(node, 'os')
                g.title = getElementData(node, 'title')
                g.put()
                logging.info(g.title)

                sg = StudentGame()
                sg.student = s
                sg.game = g
                sg.rating = getElementData(node, 'rating')
                sg.comment = getElementData(node, 'comment')
                sg.put()
                logging.info("added link")
            

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

