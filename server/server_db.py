import cherrypy
import jinja2
import json
import os
import uuid

import hangman_database
import hangman_game

# import r package
from rpy2.robjects import r
from rpy2.robjects.packages import importr
print "import R"

# tats = importr("stats")
# base = importr('base')
# my_data = r['read.csv']('../database/crime2015.csv')


# Build Jinja2 environment specifying where to load template files.
_JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
      os.path.join(os.path.dirname(__file__), '../template')))


class WrongPasswordException(Exception):
  def __init__(self, username):
    super(WrongPasswordException, self).__init__(
      'password for %s is not correct' % username)


class UserNotFoundException(Exception):
  def __init__(self, username):
    super(UserNotFoundException, self).__init__(
      'username %s does not exist' % username)


class GameNotFoundForUserException(Exception):
  def __init__(self, game_id):
    super(GameNotFoundForUserException, self).__init__(
      'game_id %s does not exist for given user' % game_id)


class HangmanServer(object):
  def __init__(self):
    self._db = hangman_database.HangmanDatabase()

  @cherrypy.expose
  def index(self):
    template = _JINJA_ENVIRONMENT.get_template('index.html')
    return template.render()

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.json_in()  
  def search(self):
    """
    search for the result with four parameters

    """
    result = {"operation": "request", "result": "success"}
    input_json = cherrypy.request.json
    value = input_json["my_key"]
    print "-------------> here!"
    return result

config = {
  # Set up the directory for static files.
  '/static': {
    'tools.staticdir.on': True,
    'tools.staticdir.dir':
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static'),
  }
}

# Create a CherryPy server object.
app = cherrypy.tree.mount(HangmanServer(), config=config)

if __name__ == '__main__':
  # Start the CherryPy server.
  # Note: Only execute this command in the main scope to prevent Google App
  # Engine from executing it. GAE has its own mechanism to start a server.
  cherrypy.quickstart(app)
