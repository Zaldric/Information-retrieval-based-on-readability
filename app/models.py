from sqlalchemy import CheckConstraint
from app import db


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    indexed = db.Column(db.Integer, index=True, unique=False)
    language = db.Column(db.String(3), index=True, unique=False)
    CheckConstraint('indexed == 1 OR indexed == 0')

    def __repr__(self):
        return '<{}, {}, {}, {}>'.format(self.id, self.name, self.indexed, self.language)


class BookThemes(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    theme_id = db.Column(db.String(30), db.ForeignKey('themes.id'), primary_key=True)

    def __repr__(self):
        return '<{} - {}>'.format(self.book_id, self.theme_id)


class Themes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(30), index=True, unique=True)

    def __repr__(self):
        return '{}, {}>'.format(self.id, self.theme)


class Model:

    @staticmethod
    def get_themes():
        themes = Themes.query.all()
        if themes:
            return themes
        else:
            return None

    @staticmethod
    def get_books():
        return Books.query.all()

    @staticmethod
    def get_books_for_language(language):
        return Books.query.filter((Books.language == language)).all()

    @staticmethod
    def get_book_themes(book_id):
        return BookThemes.query.filter((BookThemes.book_id == book_id)).all()

    @staticmethod
    def add_book(book, lang):
        db.session.add(Books(name=book, indexed=0, language=lang))
        db.session.commit()

    @staticmethod
    def add_theme_book(book_id, theme_id):
        db.session.add(BookThemes(book_id=book_id, theme_id=theme_id))
        db.session.commit()

    @staticmethod
    def get_books_for_index():
        books = Books.query.all()
        books_to_index = list()

        for item in books:
            if item.indexed == 0:
                books_to_index.append(item.name)

        return books_to_index

    @staticmethod
    def index_book(book_id):
        entry = Books.query.get(book_id)
        entry.indexed = 1
        db.session.commit()

    @staticmethod
    def is_uploaded(book):
        first, second = False, False
        exists = db.session.query(db.exists().where(Books.name == (book + '.txt'))).scalar()
        if not exists:
            first = True

        exists = db.session.query(db.exists().where(Books.name == (book + '.epub'))).scalar()
        if not exists:
            second = True

        if first and second:
            return True
        else:
            return False

