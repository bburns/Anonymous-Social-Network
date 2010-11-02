from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

class MainPage(webapp.RequestHandler):
    """
    Request handler for main page (index.html). 
    """
    def get(self):
        """
        Return the main page (index.html)
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/index.html')
        self.response.out.write(template.render(path, template_values, True))


