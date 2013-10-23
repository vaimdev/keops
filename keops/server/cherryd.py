# CherryPy daemon module
# This module runs keops/django application as CherryPy WSGI server
import cherrypy
from cherrypy.process import plugins

class Server(object):

    def run(self):
        e = cherrypy.engine
        e.start()
        e.block()
