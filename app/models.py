from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    language = db.Column(db.String(3), index=True, unique=False)
    themes = db.relationship('Themes', backref='thematic', lazy='dynamic')

    def __repr__(self):
        return '<Book {}: {}>'.format(self.name, self.language)


class Book_Themes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    theme_id = db.Column(db.String(30), db.ForeignKey('themes.id'), primary_key=True)

    def __repr__(self):
        return '<{} - {}>'.format(self.user_id, self.theme_id)


class Themes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(30), index=True, unique=True)
    books = db.relationship('Books', backref='thematic_books', lazy='dynamic')

    def __repr__(self):
        return '<Theme: {}>'.format(self.theme)
