import math
import os
from flask import render_template, redirect, url_for, request, send_file
from flask_babel import refresh
from werkzeug.utils import secure_filename
from app import app
from app.forms import QueryForm, UploadDocumentForm
from app.__init__ import MODEL
from src.IndexFileCreator import IndexFileCreator
from src.QuerySearch import QuerySearch
from flask_babel import _

THEMES = MODEL.get_themes()

# TODO Ver que pollas pasa con el índice me da que hay algo que no hace bien.
# TODO Hay palabras que por alguna razón no aparecen cuando realmente si que están presentes.
# TODO Cuando se suben varios archivos solo el primero se sube correctamente.
# TODO Cambios en los botones al ordenar los resultados, para que se vea visualmente cuál es la ordenación actual.
# TODO Indexación en Inglés.
# TODO Pantalla inicial de la aplicación (lista de libros indexados con sus temáticas).
# TODO Pantalla de edición de temáticas.
# TODO Reset de los resultados al cambiar de pantalla.
# TODO Crontap para la indexación viernes 12 noche.


def calculate_range(total_elements, page, maximum_pages):
    if total_elements < app.config['BOOKS_PER_PAGE']:
        return 0, total_elements - 1

    if page == maximum_pages:
        return (page - 1) * app.config['BOOKS_PER_PAGE'], total_elements - 1

    return (page - 1) * app.config['BOOKS_PER_PAGE'], (page * app.config['BOOKS_PER_PAGE']) - 1


def get_theme_name(theme_id):
    for theme in THEMES:
        if theme.id == theme_id:
            return theme.theme


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    books = MODEL.get_books_for_language(app.config['SELECTED_LANGUAGE'])
    theme_books = list()
    page = request.args.get('page', 1, type=int)
    maximum_pages = math.ceil(len(books) / app.config['BOOKS_PER_PAGE'])
    books_range = calculate_range(len(books), page, maximum_pages)

    for book in books:
        themes = ''
        for theme in MODEL.get_book_themes(book.id):
            themes += get_theme_name(int(theme.theme_id)) + ', '
        theme_books.append(themes)

    return render_template('index.html', page=page, maximum_pages=maximum_pages,
                           books=zip(books[books_range[0]:books_range[1]], theme_books[books_range[0]:books_range[1]]))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = QueryForm()
    page = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'similarity', type=str)
    themes = list()
    errors = list()

    for theme in THEMES:
        themes.append((theme.id, theme.theme))

    form.theme.choices = themes

    if form.is_submitted():
        app.config['selected_themes'] = selected_themes = form.theme.data

        if not form.theme.data:
            errors.append(_('Debe seleccionar al menos una temática.'))
            app.config['errors'] = errors

        if errors:
            return render_template('search.html', form=form, model=THEMES, errors=errors, selected_themes=selected_themes)

        if form.query.data != '':
            app.config['query'] = form.query.data
            app.config['ranking'] = QuerySearch(app.config['SELECTED_LANGUAGE'], form.query.data).get_ranks()
        else:
            return render_template('search.html', query='', form=form, model=THEMES, errors=errors, selected_themes=selected_themes)

    if 'ranking' in app.config:

        if app.config['ranking'] is None:
            return render_template('search.html', form=form, model=THEMES, errors=errors, selected_themes=app.config['selected_themes'])

        form.query.data = app.config['query']
        if mode == 'similarity':
            maximum_pages = math.ceil(len(app.config['ranking']['similarity_rank']) / app.config['BOOKS_PER_PAGE_IN_SEARCH'])

            if page > maximum_pages:
                page = maximum_pages

            ranking_range = calculate_range(len(app.config['ranking']['similarity_rank']), page, maximum_pages)

            return render_template('search.html', form=form, model=THEMES, errors=errors, mode=mode,
                                   selected_themes=app.config['selected_themes'],
                                   ranking=app.config['ranking']['similarity_rank'][ranking_range[0]:ranking_range[1]],
                                   page=page, maximum_pages=maximum_pages)
        else:
            maximum_pages = math.ceil(len(app.config['ranking']['readability_rank']) / app.config['BOOKS_PER_PAGE'])

            if page > maximum_pages:
                page = maximum_pages

            ranking_range = calculate_range(len(app.config['ranking']['readability_rank']), page, maximum_pages)

            return render_template('search.html', form=form, model=THEMES, errors=errors, mode=mode,
                                   selected_themes=app.config['selected_themes'],
                                   ranking=app.config['ranking']['readability_rank'][ranking_range[0]:ranking_range[1]],
                                   page=page, maximum_pages=maximum_pages)
    else:
        return render_template('search.html', query='', form=form, model=THEMES)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadDocumentForm()
    themes = list()
    errors = list()
    existing_files = list()

    for theme in THEMES:
        themes.append((theme.id, theme.theme))

    form.theme.choices = themes

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

        f = form.upload_files.data
        invalid_files = list()
        saved_files = list()

        for file in files:
            filename = secure_filename(file.filename)
            if '.txt' in filename or '.epub' in filename:
                if valid_theme:
                    if MODEL.is_uploaded(filename.split('.')[0]):
                        f.save(os.path.join(app.root_path, 'corpus', filename))
                        saved_files.append(filename)
                    else:
                        existing_files.append(filename)
                        continue
            else:
                invalid_files.append(filename)

        if invalid_files:
            message = _('Sólo se admiten archivos en formato .txt o .pub, compruebe la extensión de los siguientes archivos e inténtelo de nuevo: ')
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
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes, errors=errors, existing_files=existing_files)
        else:
            success = _('Los archivos se han procesado correctamente')
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes, success=success)

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
    return send_file('corpus/' + filename, attachment_filename=filename)


@app.route('/language/', defaults={'lang': 'es'})
@app.route('/language/<previous>/<lang>')
def language(previous, lang):
    if lang in app.config['LANGUAGES'] and app.config['SELECTED_LANGUAGE'] != lang:
        app.config['SELECTED_LANGUAGE'] = lang
        refresh()
    return redirect(url_for(previous))
