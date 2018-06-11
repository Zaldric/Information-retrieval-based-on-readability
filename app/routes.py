import math
import os
from flask import render_template, redirect, url_for, request, send_file
from flask_babel import refresh
from werkzeug.utils import secure_filename
from app import app
from app.forms import QueryForm, UploadDocumentForm, UpdateThemesForm
from app.__init__ import MODEL
from src.IndexFileCreator import IndexFileCreator
from src.QuerySearch import QuerySearch
from flask_babel import _

THEMES = MODEL.get_themes(app.config['SELECTED_LANGUAGE'])
THEME_CHOICES = list()

for theme in THEMES:
    THEME_CHOICES.append((theme.id, theme.theme))


def calculate_range(total_elements, page, maximum_pages):
    if total_elements < app.config['BOOKS_PER_PAGE']:
        return 0, total_elements - 1

    if page == maximum_pages:
        return (page - 1) * app.config['BOOKS_PER_PAGE'], total_elements - 1

    return (page - 1) * app.config['BOOKS_PER_PAGE'], (page * app.config['BOOKS_PER_PAGE']) - 1


def get_theme_name(theme_id):
    for book_theme in THEMES:
        if book_theme.id == theme_id:
            return book_theme.theme


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    app.config.pop('ranking', None)
    app.config.pop('query', None)
    app.config.pop('query', None)
    books = MODEL.get_books_for_language(app.config['SELECTED_LANGUAGE'])
    theme_books = list()
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', '#', type=str)
    maximum_pages = math.ceil(len(books) / app.config['BOOKS_PER_PAGE'])
    books_range = calculate_range(len(books), page, maximum_pages)
    index_button = False
    are_books = False

    for book in books:
        are_books = True
        themes = ''
        for book_theme in MODEL.get_book_themes(book.id):
            themes += get_theme_name(int(book_theme.theme_id)) + ', '
        theme_books.append(themes)

        if book.indexed == 0:
            index_button = True

    if sort == 'ASC':
        books = sorted(books, key=lambda x: x.name)
    elif sort == 'DESC':
        books = sorted(books,  key=lambda x: x.name, reverse=True)

    book_list = list()
    for i in range(books_range[0], books_range[1] + 1):
        book_list.append((books[i], theme_books[i]))

    return render_template('index.html', page=page, maximum_pages=maximum_pages, index_button=index_button, sort=sort,
                           are_books=are_books, books=book_list)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = QueryForm()
    page = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'similarity', type=str)

    form.theme.choices = THEME_CHOICES

    if form.is_submitted():
        app.config['selected_themes'] = selected_themes = form.theme.data

        if form.query.data != '':
            books_by_themes = MODEL.get_thematic_books(selected_themes) if selected_themes else None

            app.config['query'] = form.query.data
            app.config['ranking'] = QuerySearch(app.config['SELECTED_LANGUAGE'], form.query.data,
                                                books_by_themes).get_ranks()
        else:
            return render_template('search.html', query='', form=form, model=THEMES, selected_themes=selected_themes)

    if 'ranking' in app.config:

        if app.config['ranking'] is None:
            return render_template('search.html', form=form, model=THEMES,
                                   selected_themes=app.config['selected_themes'])

        form.query.data = app.config['query']
        if mode == 'similarity':
            maximum_pages = math.ceil(
                len(app.config['ranking']['similarity_rank']) / app.config['BOOKS_PER_PAGE_IN_SEARCH'])

            if page > maximum_pages:
                page = maximum_pages

            ranking_range = calculate_range(len(app.config['ranking']['similarity_rank']), page, maximum_pages)

            return render_template('search.html', form=form, model=THEMES, mode=mode,
                                   selected_themes=app.config['selected_themes'],
                                   ranking=app.config['ranking']['similarity_rank'][ranking_range[0]:ranking_range[1]],
                                   page=page, maximum_pages=maximum_pages)
        else:
            if app.config['SELECTED_LANGUAGE'] == 'en':
                ranking = list(reversed(app.config['ranking']['readability_rank']))
            else:
                ranking = app.config['ranking']['readability_rank']

            maximum_pages = math.ceil(len(ranking) / app.config['BOOKS_PER_PAGE'])

            if page > maximum_pages:
                page = maximum_pages

            ranking_range = calculate_range(len(ranking), page, maximum_pages)

            return render_template('search.html', form=form, model=THEMES, mode=mode,
                                   selected_themes=app.config['selected_themes'],
                                   ranking=ranking[ranking_range[0]:ranking_range[1]],
                                   page=page, maximum_pages=maximum_pages)
    else:
        return render_template('search.html', query='', form=form, model=THEMES)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    app.config.pop('ranking', None)
    app.config.pop('query', None)
    app.config.pop('query', None)
    form = UploadDocumentForm()
    errors = list()
    existing_files = list()

    form.theme.choices = THEME_CHOICES

    if form.is_submitted():
        books = MODEL.get_books()
        files = request.files.getlist("upload_files")
        selected_themes = form.theme.data
        book_id = len(books) + 1

        if not files:
            errors.append(_('Debe seleccionar al menos un fichero.'))

        if not form.theme.data:
            valid_theme = False
            errors.append(_('Debe seleccionar al menos una temática.'))
        else:
            valid_theme = True

        invalid_files = list()
        saved_files = list()

        for file in files:
            filename = secure_filename(file.filename)
            if '.txt' in filename or '.epub' in filename:
                if valid_theme:
                    if MODEL.is_uploaded(filename.split('.')[0]):
                        file.save(os.path.join(app.root_path, 'corpus/' + app.config['SELECTED_LANGUAGE'], filename))
                        saved_files.append(filename)
                    else:
                        existing_files.append(filename)
                        continue
            else:
                invalid_files.append(filename)

        if invalid_files:
            message = _(
                'Sólo se admiten archivos en formato .txt o .pub, compruebe la extensión de los siguientes archivos e inténtelo de nuevo: ')
            for invalid_file in invalid_files:
                message += invalid_file + ', '
            errors.append(message[:-2])

        if saved_files:
            for saved_file in saved_files:
                MODEL.add_book(saved_file, app.config['SELECTED_LANGUAGE'])

                for theme in selected_themes:
                    MODEL.add_theme_book(book_id, int(theme))
                book_id += 1

        if existing_files:
            errors.append(_('Los siguientes libros ya están registrados en el sistema y no se han procesado:'))

        if errors:
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes,
                                   errors=errors, existing_files=existing_files)
        else:
            success = _('Los archivos se han procesado correctamente')
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes,
                                   success=success)

    return render_template('upload.html', form=form, model=THEMES)


@app.route('/update_index')
def update_index():
    books_for_index = MODEL.get_books_for_index()
    books = MODEL.get_books()

    if books_for_index:
        instance = IndexFileCreator(app.config['SELECTED_LANGUAGE'], books_for_index)
        instance.save_index()

        for file in instance.get_processed_files():
            for book in books:
                if book.name == file:
                    book_id = book.id

            MODEL.index_book(book_id)

        return render_template('update_index.html', instance=instance.get_unprocessed_files())
    else:
        return render_template('update_index.html', instance=None)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file('corpus/' + app.config['SELECTED_LANGUAGE'] + '/' + filename, attachment_filename=filename)


@app.route('/update_themes/')
@app.route('/update_themes/<book_id>', methods=['GET', 'POST'])
def update_themes(book_id):
    book = MODEL.get_book(book_id)
    form = UpdateThemesForm()
    page = request.args.get('page', '1', type=str)

    if form.is_submitted():

        if not form.theme.data:
            error = _('Debe seleccionar al menos una temática.')
            selected_themes = [book.theme_id for book in MODEL.get_book_themes(book_id)]
            form.theme.choices = THEME_CHOICES

            return render_template('update_themes.html', error=error, book=book, form=form,
                                   selected_themes=selected_themes, page=page)

        MODEL.update_themes(book_id, form.theme.data)
        return redirect('index?page=' + page)

    if book:
        selected_themes = [book.theme_id for book in MODEL.get_book_themes(book_id)]

        form.theme.choices = THEME_CHOICES
        return render_template('update_themes.html', form=form, model=THEMES, book=book,
                               selected_themes=selected_themes, page=page)

    return render_template('update_themes.html')


@app.route('/language/', defaults={'lang': 'es'})
@app.route('/language/<previous>/<lang>')
def language(previous, lang):
    if lang in app.config['LANGUAGES'] and app.config['SELECTED_LANGUAGE'] != lang:
        app.config.pop('ranking', None)
        app.config.pop('query', None)
        app.config.pop('query', None)
        app.config['SELECTED_LANGUAGE'] = lang

        global THEMES, THEME_CHOICES
        THEMES = MODEL.get_themes(app.config['SELECTED_LANGUAGE'])
        THEME_CHOICES.clear()

        for language_theme in THEMES:
            THEME_CHOICES.append((language_theme.id, language_theme.theme))

        refresh()
    return redirect(url_for(previous))
