import os
from utils.sessions import Session
from models import *

def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), '../templates/' + filename)
    if not os.path.isfile(filepath):
        handler.response.out.write("Invalid template file: " + filename)
        return False

    # copy the dictionary, so we can add things to it
    newdict = dict(values)
    newdict['path'] = handler.request.path
    newdict['recentClasses'] = Class.get_by_date()
    newdict['recentBooks'] = Book.get_by_date()
    newdict['recentPapers'] = Paper.get_by_date()
    newdict['recentInternships'] = Internship.get_by_date()
    newdict['recentPlaces'] = Place.get_by_date()
    newdict['recentGames'] = Game.get_by_date()
    handler.session = Session()
    if 'username' in handler.session:
        newdict['username'] = handler.session['username']

    if 'student_id' in handler.session:
        newdict['student_id'] = handler.session['student_id']
    
    if 'admin' in handler.session:
        newdict['admin'] = handler.session['admin']


    s = template.render(filepath, newdict)
    handler.response.out.write(s)
    return True
