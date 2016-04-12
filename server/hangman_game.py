import os
import random


LEVEL_BASIC = 'B'
LEVEL_ADVANCED = 'A'

_WORDS_FILE_PATH = os.path.join(
  os.path.dirname(os.path.realpath(__file__)), '../data/words_en.txt')
_ADVANCED_WORDS_FILES = [
  'w2_1000.txt',
  'w3_1000.txt',
  'w4_1000.txt',
  'w5_1000.txt',
]
_ADVANCED_WORDS_FILE_PATHS = [
  os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/', word_file)
  for word_file in _ADVANCED_WORDS_FILES]

_WORDS = []
_ADVANCED_WORDS = []


class HangmanGame(object):
  def __init__(self, word, level, guess_word=None, failure_times=0, finished=False):
    self.word = word
    self.level = level
    if guess_word:
      self.guess_word = guess_word
    else:
      self.guess_word = '_' * len(word)
    self.failure_times = failure_times
    self.finished = finished

  def guess(self, letter):
    is_right = False
    sguess_word = list(self.guess_word)
    for index, c in enumerate(self.word):
      if c == letter:
        sguess_word[index] = letter
        is_right = True
    self.guess_word = ''.join(sguess_word)

    if not is_right:
      self.failure_times += 1

    if '_' not in self.guess_word:
      self.finished = True

    return is_right


def _load_words():
  global _WORDS
  if _WORDS:
    return

  # Load words.
  _WORDS = []
  f = open(_WORDS_FILE_PATH, 'r')
  for line in f:
    line = line.strip()
    _WORDS.append(line)
  f.close()


def _load_advanced_words():
  global _ADVANCED_WORDS
  if _ADVANCED_WORDS:
    return

  # Load words.
  _ADVANCED_WORDS = []
  for file_path in _ADVANCED_WORDS_FILE_PATHS:
    f = open(file_path, 'r')
    for line in f:
      line = line.strip()
      parts = line.split()
      word = ' '.join(parts[1:])
      _ADVANCED_WORDS.append(word)
    f.close()


def generate_game():
  _load_words()
  index = random.randint(0, len(_WORDS) - 1)
  return HangmanGame(_WORDS[index], LEVEL_BASIC)


def generate_advanced_game():
  _load_advanced_words()
  index = random.randint(0, len(_ADVANCED_WORDS) - 1)
  return HangmanGame(_ADVANCED_WORDS[index], LEVEL_ADVANCED)
