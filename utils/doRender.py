import os
from utils.sessions import Session
from models import *

def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), '../views/' + filename)
    if not os.path.isfile(filepath):
        handler.response.out.write("Invalid template file: " + filename)

    # copy the dictionary, so we can add things to it
    newvalues = dict(values)
    
    newvalues['path'] = handler.request.path
    newvalues['recentClasses'] = Class.get_by_date()
    newvalues['recentBooks'] = Book.get_by_date()
    newvalues['recentPapers'] = Paper.get_by_date()
    newvalues['recentInternships'] = Internship.get_by_date()
    newvalues['recentPlaces'] = Place.get_by_date()
    newvalues['recentGames'] = Game.get_by_date()
    
    # set the session object for this handler - will pass cookie to browser
    handler.session = Session()
    
    # add some more values to the dictionary, useful to templates
    if 'username' in handler.session:
        newvalues['username'] = handler.session['username']
    if 'student_id' in handler.session:
        newvalues['student_id'] = handler.session['student_id']
    if 'admin' in handler.session:
        newvalues['admin'] = handler.session['admin']

    # render the template
    s = template.render(filepath, newvalues)
    handler.response.out.write(s)
