import cherrypy
import json
import uuid

import hangman_game


class HangmanServer(object):
  def __init__(self):
    self._email_to_game_ids = {}
    self._games = {}

  @cherrypy.expose
  def start_game(self, email):
    game_id = str(uuid.uuid4())
    self._email_to_game_ids[email] = game_id
    self._games[game_id] = hangman_game.generate_game()
    return game_id

  @cherrypy.expose
  def get_current_progress(self, game_id):
    if game_id not in self._games:
      return json.dumps({
        'message': 'game_id %s not found' % game_id,
      })

    game = self._games[game_id]
    return json.dumps({
      'guess_word': game.guess_word,
      'failure_times': game.failure_times,
      'finished': game.finished,
      'message': '',
    })

  @cherrypy.expose
  def guess(self, game_id, letter):
    if game_id not in self._games:
      return json.dumps({
        'message': 'game_id %s not found' % game_id,
      })

    game = self._games[game_id]
    is_right = game.guess(letter)
    return json.dumps({
      'guess_word': game.guess_word,
      'failure_times': game.failure_times,
      'finished': game.finished,
      'is_right': is_right,
      'message': '',
    })

  @cherrypy.expose
  def index(self):
    return "Welcome to Hangman Game!"

app = cherrypy.tree.mount(HangmanServer())

if __name__ == '__main__':
  cherrypy.quickstart(app)
