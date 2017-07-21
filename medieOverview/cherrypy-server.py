import cherrypy
from medieOverview.wsgi import application
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings = {
    "/static": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": os.path.join(BASE_DIR, "staticfiles")
    }
}
class Root(object):
    pass

cherrypy.tree.mount(Root(), "/", settings)
cherrypy.tree.graft(application, '/')

cherrypy.config.update({'server.socket_port': 9090, 'server.socket_host': '0.0.0.0',})

cherrypy.engine.start()
cherrypy.engine.block()