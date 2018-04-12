from app import app, db
from app.models import Book, Book_Themes, Themes


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Book': Book, 'Book_Themes': Book_Themes, 'Themes': Themes}
