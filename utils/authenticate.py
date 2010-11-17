from utils.sessions import Session
from utils.doRender import doRender

def authenticate(f):
    def check_session(self):
        session = Session()
        if 'student_id' not in session:
            return doRender(self,'not_auth.html')
        else:
            return f(self)
    return check_session
