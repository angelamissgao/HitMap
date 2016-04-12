import MySQLdb
import MySQLdb.cursors
import os


_INSTANCE_NAME = 'hangman-fbwolf:hangman'

class HangmanDatabase(object):
  def __init__(self):
    self._connect_db()

  def _connect_db(self):
    """Connect to MySQL database."""
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
      # Connect to cloud SQL.
      self._db = MySQLdb.connect(
        unix_socket='/cloudsql/' + _INSTANCE_NAME, db='hangman',
        user='root', charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
      # Alternatively, connect to a Google Cloud SQL instance using:
      # db = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance',
      # port=3306, user='root', charset='utf8')
    else:
      # Connect to local MySQL.
      self._db = MySQLdb.connect(
        host='127.0.0.1', port=3306, db='hangman', user='root', passwd='19880828',
        charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)

  def _execute_sql(self, func):
    """Execute SQL command.

    If the connection was lost when executing the command, we'll reconnect the
    Database and then execute the command again.

    Args:
      func: A function which contains the SQL command to execute.

    Returns:
      The return value of func.
    """
    try:
      return func()
    except MySQLdb.OperationalError:
      self._connect_db()
      return func()

  def insert_user(self, username, password):
    """Insert a user.

    Args:
      username: A str, the user's username.
      password: A str, the user's password.

    Returns:
      The ID of the newly inserted user.
    """
    def _insert_user():
      cursor = self._db.cursor()
      cursor.execute(
        """
        INSERT INTO user(username, password)
        VALUES (%s, %s)
        """,
        (username, password))
      self._db.commit()
      row_id = cursor.lastrowid
      cursor.close()
      return row_id

    return self._execute_sql(_insert_user)

  def get_user_by_username(self, username):
    """Get a user row by username.

    Args:
      username: A str, the user's username.

    Returns:
      The user's row in DB.
    """
    def _get_user_by_username():
      cursor = self._db.cursor()
      cursor.execute(
        """
        SELECT id, password
        FROM user
        WHERE username = %s
        """,
        (username,))
      row = cursor.fetchone()
      cursor.close()
      return row
    return self._execute_sql(_get_user_by_username)

  def insert_game(self, user_id, game_id, game):
    """Insert a game.

    Args:
      user_id: An int, the ID of the user.
      game_id: A str, the ID of the game.
      game: A hangman_game.Game, the inserted game.
    """
    def _insert_game():
      cursor = self._db.cursor()
      cursor.execute(
        """
        INSERT INTO game(user_id, game_id, word, guess_word, failure_times,
                         finished, level)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, game_id, game.word, game.guess_word,
         game.failure_times, game.finished, game.level))
      self._db.commit()
      row_id = cursor.lastrowid
      cursor.close()
    self._execute_sql(_insert_game)

  def get_game_by_game_and_user(self, game_id, user_id):
    """Get game row by game external ID and user ID.

    Args:
      game_id: A str, the game ID.
      user_id: An int, the user ID.

    Returns:
      The game row.
    """
    def _get_game_by_game_and_user():
      cursor = self._db.cursor()
      cursor.execute(
        """
        SELECT word, guess_word, failure_times, finished, level
        FROM game
        WHERE game_id = %s AND user_id = %s
        """,
        (game_id, user_id))
      row = cursor.fetchone()
      cursor.close()
      return row
    return self._execute_sql(_get_game_by_game_and_user)

  def update_game(self, game_id, game):
    """Update a game.

    Args:
      game_id: A str, the game ID.
      game: A hangman_game.Game, the game to update.
    """
    def _update_game():
      cursor = self._db.cursor()
      cursor.execute(
        """
        UPDATE game
        SET guess_word = %s,
            failure_times = %s,
            finished = %s
        WHERE game_id = %s
        """,
        (game.guess_word, game.failure_times, game.finished, game_id))
      self._db.commit()
      cursor.close()
    self._execute_sql(_update_game)

  def get_user_stats(self, level, page=0, page_size=10):
    """Get users' game statistics for given page.

    The statistics include the user ID, average failures and total number of
    games user have played.

    Args:
      level: A str, the game level. Must be one of hangman_game.LEVEL_*.
      page: An int, the current page number.
      page_size: An int, number of users per page.

    Returns:
      The statistics row.
    """
    def _get_user_stats():
      cursor = self._db.cursor()
      cursor.execute(
        """
        SELECT user_id, avg(failure_times) AS avg_failures, count(*) AS total_games
        FROM game
        WHERE finished = 1
          AND level = %s
        GROUP BY user_id
        ORDER BY avg_failures ASC
        LIMIT %s, %s
        """, (level, page_size*page, page_size))
      rows = cursor.fetchall()
      cursor.close()
      return rows
    return self._execute_sql(_get_user_stats)

  def get_user_count_for_level(self, level):
    """Get user count that have played a game for given level.

    Args:
      level: A str, the game level. Must be one of hangman_game.LEVEL_*.

    Returns:
      The total user count.
    """
    def _get_user_count_for_level():
      cursor = self._db.cursor()
      cursor.execute(
        """
        SELECT COUNT(DISTINCT(user_id)) AS count_user
        FROM game
        WHERE finished = 1
          AND level = %s
        """, (level))
      row = cursor.fetchone()
      cursor.close()
      return row['count_user']
    return self._execute_sql(_get_user_count_for_level)

  def get_all_users(self):
    """Get all users.

    Returns:
      A list of user rows which contain id and username.
    """
    def _get_all_users():
      cursor = self._db.cursor()
      cursor.execute(
        """
        SELECT id, username
        FROM user
        """)
      rows = cursor.fetchall()
      cursor.close()
      return rows
    return self._execute_sql(_get_all_users)
