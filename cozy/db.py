import os
from peewee import *
from xdg import *

# first we get the data home and find the database if it exists
data_dir = BaseDirectory.xdg_data_home + "/cozy/"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

db = SqliteDatabase(data_dir + "cozy.db")

class BaseModel(Model):
  """
  The BaseModel is the base class for all db tables.
  """
  class Meta:
    """
    The Meta class encapsulates the db object
    """
    database = db

class Book(BaseModel):
  """
  Book represents an audio book in the database.
  """
  name = CharField()
  author = CharField()
  reader = CharField()
  position = IntegerField()
  rating = IntegerField()
  cover = BlobField(null=True)

class Track(BaseModel):
  """
  Track represents a track from an audio book in the database.
  """
  name = CharField()
  number = IntegerField()
  disk = IntegerField()
  position = IntegerField()
  book = ForeignKeyField(Book)
  file = CharField()
  length = FloatField()
  modified = IntegerField()

class Settings(BaseModel):
  """
  Settings contains all settings that are not saved in the gschema.
  """
  path = CharField()
  first = BooleanField(default=True)

def InitDB():
  db.connect()
  # Create tables only when not already present
  #                                           |
  db.create_tables([Track, Book, Settings], True)

  if (Settings.select().count() == 0):
    Settings.create(path = "")

def Books():
  """
  Find all books in the database

  :return: all books
  """
  return Book.select()

def Search(search):
  return Track.select().where(search in Track.name)

# Return ordered after Track ID / name when not available
def Tracks(book):
  """
  Find all tracks that belong to a given book

  :param book: the book object
  :return: all tracks belonging to the book object
  """
  return Track.select().join(Book).where(Book.id == book.id).order_by(Track.disk, Track.number, Track.name)

def CleanDB():
  """
  Delete everything from the database except settings.
  """
  q = Track.delete()
  q.execute()
  q = Book.delete()
  q.execute()

def SecondsToStr(seconds):
  """
  Converts seconds to a string with the following apperance:
  hh:mm:ss

  :param seconds: The seconds as float
  """
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)

  if (h > 0):
    result = "%d:%02d:%02d" % (h, m, s)
  elif (m > 0):
    result = "%02d:%02d" % (m, s)
  else:
    result = "00:%02d" % (s)

  return result