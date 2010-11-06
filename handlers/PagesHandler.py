class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self,'index.html')

class Help(webapp.RequestHandler):
    def get(self):
        doRender(self,"help.html")

class About(webapp.RequestHandler):
    def get(self):
        doRender(self,"about.html")
