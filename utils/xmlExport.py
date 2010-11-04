from models import *
from xml.dom.minidom import Document
from xml.dom import Node


def xmlExport(students):
    """
    Exports the given iterable of students to xml.
    Input: iterable of Student objects (could be a list, or a query)
    Output: xml string
    """
    dom = Document()
    dom.appendChild(dom.createElement("students"))
    rootNode = dom.childNodes[0]
    for student in students:
        #print student
        #print student.to_xml()
        # trying to get properties and values through reflection
        #for k,v in type(student).properties().items():
        #    print k,v.toString()
        appendModel(dom, rootNode, student)
    return dom.toxml()


def appendModel(dom, node, model):
    """
    Append the given model object to the xml document at the given node.

    Input:
        dom: the xml document 
        node: the current node in the xml document
        model: the appengine model we are appending, eg a Student
    Output:
        the new node (which has been appended to the dom) 
    """

    # Get the name of this model's type, eg Student, Book, etc
    name = type(model).__name__

    # Handle each type separately
    #. this code could be defined in each model class, eg in a toXml method
    if name == 'Student':

        # create a <student></student> element, and add child elements for properties
        e = dom.createElement("student")
        node.appendChild(e)
        appendElement(dom,e,"id",model.id_)
        appendElement(dom,e,"password",model.password)

        # Now add all related objects, by calling this function recursively
        for sc in model.studentclass_set :
            cl = sc.class_
            newNode = appendModel(dom, e, cl)
            appendElement(dom, newNode, "grade", sc.grade)
            appendElement(dom, newNode, "rating", sc.rating)
            appendElement(dom, newNode, "comment", sc.comment)

        for sb in model.studentbook_set :
            b = sb.book
            newNode = appendModel(dom, e, b)
            appendElement(dom, newNode, "rating", sb.rating)
            appendElement(dom, newNode, "comment", sb.comment)

        for sp in model.studentpaper_set :
            p = sp.paper
            newNode = appendModel(dom, e, p)
            appendElement(dom, newNode, "rating", sp.rating)
            appendElement(dom, newNode, "comment", sp.comment)

        for si in model.studentinternship_set :
            i = si.internship
            newNode = appendModel(dom, e, i)
            appendElement(dom, newNode, "rating", si.rating)
            appendElement(dom, newNode, "comment", si.comment)

        for sp in model.studentplace_set :
            p = sp.place
            newNode = appendModel(dom, e, p)
            appendElement(dom, newNode, "rating", sp.rating)
            appendElement(dom, newNode, "comment", sp.comment)

        for sg in model.studentgame_set :
            g = sg.game
            newNode = appendModel(dom, e, g)
            appendElement(dom, newNode, "rating", sg.rating)
            appendElement(dom, newNode, "comment", sg.comment)
        

    elif name == 'Class':
        e = dom.createElement("class")
        node.appendChild(e)
        appendElement(dom,e,"unique",model.unique)
        appendElement(dom,e,"course_num",model.course_num)
        appendElement(dom,e,"course_name",model.course_name)
        appendElement(dom,e,"semester",model.semester)
        appendElement(dom,e,"instructor",model.instructor)

    elif name == 'Book':
        e = dom.createElement('book')
        node.appendChild(e)
        appendElement(dom,e,"isbn",model.isbn)
        appendElement(dom,e,"title",model.title)
        appendElement(dom,e,"author",model.author)

    elif name == 'Paper' :
        e = dom.createElement('paper')
        node.appendChild(e)
        appendElement(dom,e,"paper_category",model.paper_category)
        appendElement(dom,e,"title",model.title)
        appendElement(dom,e,"author",model.author)

    elif name == 'Internship' :
        e = dom.createElement('internship')
        node.appendChild(e)
        appendElement(dom,e,"place_name",model.place_name)
        appendElement(dom,e,"location",model.location)
        appendElement(dom,e,"semester",model.semester)

    elif name == 'Place' :
        place_type = model.place_type
        e = dom.createElement(place_type) # eg study_place, fun_place
        node.appendChild(e)
        appendElement(dom,e,"place_name",model.place_name)
        appendElement(dom,e,"location",model.location)
        appendElement(dom,e,"semester",model.semester)

    elif name == 'Game' :
        e = dom.createElement('game')
        node.appendChild(e)
        appendElement(dom,e,"os",model.os)
        appendElement(dom,e,"title",model.title)

    return e


def appendElement(dom, node, tagname, variable) :
    """
    Append an xml element to the document at the given node.
    Will skip the element if the value is None. 

    Example:
        appendElement(dom,e,"location","austin") will append
        "<location>austin</location" to the document model under node 'node'.
    Input:
        dom: the xml document
        node: the parent node to append to
        tagname: the name for the xml entity's tag (will be wrapped in brackets)
        variable: the contents of the xml entity
    Output:
        none. appends to the dom
    """

    #. could have an option to include empty elements, eg <Book/> or <Book></Book>
    if variable : # skip this element if it's empty
        e = dom.createElement(tagname)
        s = str(variable) if variable else ""
        data = dom.createTextNode(s)
        e.appendChild(data)
        node.appendChild(e)

