import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret@TFG_48–@jcgm#UJA-token'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    LANGUAGES = ['es', 'en']
    SELECTED_LANGUAGE = 'es'
    BOOKS_PER_PAGE = 20
    BOOKS_PER_PAGE_IN_SEARCH = 10
