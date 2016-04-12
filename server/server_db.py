import cherrypy
import jinja2
import json
import os
import uuid

import hangman_database
import hangman_game

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

  def _check_login(self, username, password):
    """Check if given user login exists.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.

    Returns:
      An int, the given user ID.

    Raises:
      WrongPasswordException: If the given password is wrong.
      UserNotFoundException: If the given user is not found.
    """
    user_row = self._db.get_user_by_username(username)
    if user_row:
      if user_row['password'] != password:
        raise WrongPasswordException(username)
      return user_row['id']
    else:
      raise UserNotFoundException(username)

  def _check_game(self, game_id, user_id):
    """Load game given game_id and user_id.

    Args:
      game_id: A str, the game ID.
      user_id: An int, the user ID.

    Returns:
      The corresponding Game.

    Raises:
      GameNotFoundForUserException: If no such game is found.
    """
    game_row = self._db.get_game_by_game_and_user(game_id, user_id)
    if game_row:
      game = hangman_game.HangmanGame(
        word=game_row['word'],
        level=game_row['level'],
        guess_word=game_row['guess_word'],
        failure_times=game_row['failure_times'],
        finished=game_row['finished'])
      return game
    else:
      raise GameNotFoundForUserException(game_id)

  @cherrypy.expose
  def start_game(self, username, password):
    """Start a basic game.

    If username doesn't exist, we will create a user with given username and
    password.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.

    Returns:
      A JSON object including the game ID.
    """
    try:
      user_id = self._check_login(username, password)
    except UserNotFoundException:
      user_id = self._db.insert_user(username, password)
    except Exception as e:
      return json.dumps({
        'message': str(e),
      })

    game_id = str(uuid.uuid4())
    game = hangman_game.generate_game()
    self._db.insert_game(user_id, game_id, game)
    return json.dumps({
      'game_id': game_id,
      'message': '',
    })

  @cherrypy.expose
  def start_advanced_game(self, username, password):
    """Start an advanced game.

    If username doesn't exist, we will create a user with given username and
    password.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.

    Returns:
      A JSON object including the game ID.
    """
    try:
      user_id = self._check_login(username, password)
    except UserNotFoundException:
      user_id = self._db.insert_user(username, password)
    except Exception as e:
      return json.dumps({
        'message': str(e),
      })

    game_id = str(uuid.uuid4())
    game = hangman_game.generate_advanced_game()
    self._db.insert_game(user_id, game_id, game)
    return json.dumps({
      'game_id': game_id,
      'message': '',
    })

  @cherrypy.expose
  def get_current_progress(self, username, password, game_id):
    """Get current progress for a given game.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.
      game_id: A str, the game ID.

    Returns:
      A JSON object including the current status of the guessing word, failure
      times, and whether the game is finished.
    """
    try:
      user_id = self._check_login(username, password)
      game = self._check_game(game_id, user_id)
    except Exception as e:
      return json.dumps({
        'message': str(e),
      })

    return json.dumps({
      'guess_word': game.guess_word,
      'failure_times': game.failure_times,
      'finished': game.finished,
      'message': '',
    })

  @cherrypy.expose
  def guess(self, username, password, game_id, letter):
    """Guess a letter for a given game.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.
      game_id: A str, the game ID.
      letter: A str, the letter to guess.

    Returns:
      A JSON object including the current status of the guessing word, failure
      times, whether the game is finished, and whether the guess is correct.
    """
    try:
      user_id = self._check_login(username, password)
      game = self._check_game(game_id, user_id)
    except Exception as e:
      return json.dumps({
        'message': str(e),
      })

    is_right = game.guess(letter)
    self._db.update_game(game_id, game)

    return json.dumps({
      'guess_word': game.guess_word,
      'failure_times': game.failure_times,
      'finished': game.finished,
      'is_right': is_right,
      'message': '',
    })

  @cherrypy.expose
  def dashboard(self, level='B', page='0', page_size='10'):
    """Render dashboard page.

    Args:
      level: A str, the game level. Must be one of hangman_game.LEVEL_*.
      page: A str, the current page number. Must be able to cast into integer.
      page_size: A str, number of users per page. Must be able to cast into
        integer.

    Returns:
      The rendered page.
    """
    page = int(page)
    page_size = int(page_size)

    # Get all users.
    users = self._db.get_all_users()
    username_by_user_id = dict(
      [(user['id'], user['username']) for user in users])

    # Get user stats and fill in necessary information.
    user_stats = self._db.get_user_stats(level, page=page, page_size=page_size)
    for index, user_stat in enumerate(user_stats):
      user_stat['rank'] = page * page_size + index + 1
      user_stat['username'] = username_by_user_id[user_stat['user_id']]

    # Get max page number.
    user_count = self._db.get_user_count_for_level(level)
    max_page = (user_count - 1) / page_size
    print user_count, max_page

    template_values = {
      'user_stats': user_stats,
      'page': page,
      'page_size': page_size,
      'max_page': max_page,
      'level': level,
    }
    template = _JINJA_ENVIRONMENT.get_template('dashboard.html')
    return template.render(template_values)

  @cherrypy.expose
  def index(self):
    return 'Welcome to HitMap'


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
