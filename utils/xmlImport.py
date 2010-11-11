from models import *
from xml.dom import minidom


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


"""
Looking at the XML in binary.xml, you might think that the grammar has only two child nodes, the two ref elements. But you're missing something: the carriage returns! After the '<grammar>' and before the first '<ref>' is a carriage return, and this text counts as a child node of the grammar element. Similarly, there is a carriage return after each '</ref>'; these also count as child nodes. So grammar.childNodes is actually a list of 5 objects: 3 Text objects and 2 Element objects.
ugh


change to iterate over child nodes, add to a dictionary, then pull out the values you want?

getElementsByTagName finds all children of a given name, no matter how deep, thus working recursively. This is usually good, but can cause problems if similar nodes exist at multiple levels and the intervening nodes are important. 

> make test module=xmlImport

initially 
Ran 21 tests in 10.578s

transform1: iterate over rootNode.childNodes instead of gathering all student nodes
  Ran 21 tests in 7.835s

transform2: iterate over student childnodes, instead of searching for them
  Ran 21 tests in 7.681s

transform3: iterate over classes
  Ran 21 tests in 7.845s
  hmm, didn't help. might be the giant switch statement on properties. 
  so use a hash? 

transform4: use hash to check if element is valid property, use __setattr__ to set it
  Ran 21 tests in 7.873s
  damn

  so it looks like using getElementsByTagName is not a problem, 
  except for the top level one. 
  okay - the code is clearer with it anyway. 
  big time savings will come from ditching the xml file. 

transform5: revert to transform1
 Ran 21 tests in 7.653s

transform6: start removing the xml file tests. 
  one test down - 
  Ran 21 tests in 7.190s
  yep. 

transform7: delete *all* tables in between tests
  Ran 21 tests in 9.653s
  so doing this adds about a tenth of a second per test. bleh. 

transform8: continue removing xml file tests
  Ran 22 tests in 9.086s
  Ran 22 tests in 8.497s
  Ran 22 tests in 7.996s
  Ran 22 tests in 7.409s

  oy...


------------------

problem is - 
we get the student, set the properties, add to db. 
get a class, set the properties, add to db.
get the studentclass, set the properties, add to db. 
actually, should be okay, assuming the dom elements are in the right order. 
if not, it'll fail. but that's okay. 

um, the parser has already done the hard work - it's all in the dom now. 
we just need to iterate over the dom, 
and when you see an element you recognize, call the corresponding class import method?
eg
if e.name=='student':
    student = Student.createFromDom(e)
    student.put()

and could have a map from element name to the corresponding class
classMap = {'student': Student, 'class': Class, 'book': Book...}
cl = classMap[e.name]
o = cl.createFromDom(e)
o.put()

so just iterate over the student nodes, 
call this on them. 
then the student will handle iterating over child doms? 
alternative is doing a switch here

also use a hash for mapping properties, so don't have to do long switch statement
propMap = {'unique': 'unique', ...}
then
propname = propMap[e.name]
o.__set__(propname, propvalue)

"""



def xmlImport(dom):
    """
    Imports a dom (document object model) to a google database.
    Input: a dom, obtained by parsing an xml file, for instance. 
    Output: None. but there is a database created that you can now query.    
    """

    # cprops = ['unique','course_num','course_name','semester','instructor']
    # cpropmap = dict(zip(cprops, cprops))

    # scprops = ['grade','rating','comment']
    # scpropmap = dict(zip(scprops, scprops))


    # the root node should be a 'students' element
    rootNode = dom.firstChild

    # iterate over all student nodes

    # transform1
#    for studentNode in rootNode.getElementsByTagName('student') :
    for studentNode in rootNode.childNodes:
        #. assert this true? NO - could be an empty element (due to CR's in text!)
        #assert (studentNode.nodeName == "student")
        if studentNode.nodeName == "student":

            # transform2
            # add the student to the database
            s = Student()
            s.id_ = getElementData(studentNode, "id")
            s.password = getElementData(studentNode, "password")
            s.put()

            # s = Student()
            # #s.put()
            # for node in studentNode.childNodes:
            #     name = node.nodeName
            #     if name == "id": 
            #         s.id_ = getData(node)
            #     elif name == "password": 
            #         s.password = getData(node)
            #         # have all data, so can save it to db
            #         #s.put()

            #     # transform3
            #     elif name == "class": 
            #         c = Class()
            #         #c.put()
            #         sc = StudentClass()
            #         #sc.put()

            #         for node2 in node.childNodes:
            #             propname = node2.nodeName
            #             propvalue = getData(node2)

            #             # transform4
            #             # if propname == "unique": c.unique = propvalue
            #             # elif propname == "course_num": c.course_num = propvalue
            #             # elif propname == "course_name": c.course_name = propvalue
            #             # elif propname == "semester": c.semester = propvalue
            #             # elif propname == "instructor": c.instructor = propvalue

            #             # elif propname == "grade": sc.grade = propvalue
            #             # elif propname == "rating": sc.rating = propvalue
            #             # elif propname == "comment": sc.comment = propvalue

            #             if propname in cpropmap:
            #                 c.__setattr__(propname, propvalue)
            #             elif propname in scpropmap:
            #                 sc.__setattr__(propname, propvalue)

            #         s.put()
            #         c.put()
            #         sc.student = s
            #         sc.class_ = c
            #         sc.put()
            # s.put()


            # now look for child elements and add them also

            # class tag handler
            for node in studentNode.getElementsByTagName('class'):
                # create a class object
                # c = Class()
                # c.unique = getElementData(node, 'unique')
                # c.course_num = getElementData(node, 'course_num')
                # c.course_name = getElementData(node, 'course_name')
                # c.semester = getElementData(node, 'semester')
                # c.instructor = getElementData(node, 'instructor')
                # c.put()

                # find or add a class object
                unique = getElementData(node, 'unique')
                course_num = getElementData(node, 'course_num')
                course_name = getElementData(node, 'course_name')
                semester = getElementData(node, 'semester')
                instructor = getElementData(node, 'instructor')
                c = Class.findAdd(course_num, course_name, instructor, unique, semester)

                #create a studentClass association class
                sc = StudentClass()
                sc.student = s
                sc.class_ = c
                sc.grade = getElementData(node, 'grade')
                sc.rating = getElementData(node, 'rating')
                sc.comment = getElementData(node, 'comment')
                sc.put()                    

            # books
            for node in studentNode.getElementsByTagName('book'):

                # create a book object
                # b = Book()
                # b.isbn = getElementData(node, 'isbn')
                # b.author = getElementData(node, 'author')
                # b.title = getElementData(node, 'title')
                # b.put()

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
    #e = node.getElementsByTagName(tagname)[0].firstChild
    nodes = node.getElementsByTagName(tagname)

    if nodes:
        e = nodes[0].firstChild
	if e is None:
            return ""
        else:
            return e.data
    else:
        return ""


# def getData(node):
#     """
#     """
#     e = node.firstChild
#     if e is None:
#         return ""
#     return e.data

