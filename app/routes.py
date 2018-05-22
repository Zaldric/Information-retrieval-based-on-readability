import math
import os
from flask import render_template, redirect, url_for, request, send_file
from flask_babel import refresh
from werkzeug.utils import secure_filename
from os import listdir
from os.path import isfile, join
from app import app
from app.forms import QueryForm, UploadDocumentForm
from app.__init__ import MODEL
from src.IndexFileCreator import IndexFileCreator
from src.QuerySearch import QuerySearch
from flask_babel import _

THEMES = MODEL.get_themes()
BOOKS = MODEL.get_indexed_books()


def calculate_range(total_elements, page, maximum_pages):
    if total_elements < app.config['BOOKS_PER_PAGE']:
        return 0, total_elements - 1

    if page == maximum_pages:
        return (page - 1) * app.config['BOOKS_PER_PAGE'], total_elements - 1

    return (page - 1) * app.config['BOOKS_PER_PAGE'], (page * app.config['BOOKS_PER_PAGE']) - 1


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('search'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = QueryForm()
    themes = list()
    errors = list()

    for theme in THEMES:
        themes.append((theme.id, theme.theme))

    form.theme.choices = themes

    if form.is_submitted():
        if not form.theme.data:
            errors.append(_('Debe seleccionar al menos una temática.'))

        if form.query.data != '':
            app.config['query'] = form.query.data
            app.config['themes'] = form.theme.data
            return redirect(url_for('results'))
        else:
            if errors:
                return render_template('search.html', form=form, model=THEMES, errors=errors)

    return render_template('search.html', form=form, model=THEMES)


@app.route('/results', methods=['GET', 'POST'])
def results():
    page = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'similarity', type=str)
    ranking = QuerySearch(app.config['SELECTED_LANGUAGE'], app.config['query']).get_ranks()

    if mode == 'similarity':
        maximum_pages = math.ceil(len(ranking['similarity_rank']) / app.config['BOOKS_PER_PAGE'])

        if page > maximum_pages:
            page = maximum_pages

        ranking_range = calculate_range(len(ranking['similarity_rank']), page, maximum_pages)

        return render_template('results.html', ranking=ranking['similarity_rank'][ranking_range[0]:ranking_range[1]], page=page, maximum_pages=maximum_pages)
    else:
        maximum_pages = math.ceil(len(ranking['readability_rank']) / app.config['BOOKS_PER_PAGE'])

        if page > maximum_pages:
            page = maximum_pages

        ranking_range = calculate_range(len(ranking['readability_rank']), page, maximum_pages)

        return render_template('results.html', ranking=ranking['readability_rank'][ranking_range[0]:ranking_range[1]], page=page, maximum_pages=maximum_pages)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadDocumentForm()
    themes = list()
    errors = list()
    for theme in THEMES:
        themes.append((theme.id, theme.theme))

    form.theme.choices = themes

    if form.is_submitted():
        files = request.files.getlist("upload_files")
        selected_themes = form.theme.data

        if not files:
            errors.append(_('Debe seleccionar al menos un fichero.'))

        if not form.theme.data:
            valid_theme = False
            errors.append(_('Debe seleccionar al menos una temática.'))
        else:
            valid_theme = True

        f = form.upload_files.data
        invalid_files = list()

        for file in files:
            filename = secure_filename(file.filename)
            if '.txt' in filename or '.pub' in filename:
                if valid_theme:
                    f.save(os.path.join(app.root_path, 'corpus', filename))
            else:
                invalid_files.append(filename)

        if invalid_files:
            message = _('Sólo se admiten archivos en formato .txt o .pub, compruebe la extensión de los siguientes archivos e inténtelo de nuevo: ')
            for invalid_file in invalid_files:
                message += invalid_file + ', '
            errors.append(message[:-2])

        if errors:
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes, errors=errors)
        else:
            success = _('Los archivos se han procesado correctamente')
            return render_template('upload.html', form=form, model=THEMES, selected_themes=selected_themes, success=success)

    return render_template('upload.html', form=form, model=THEMES)


@app.route('/update_index')
def update_index():
    # When the system have the databse book implemented, change and just load the books in the database
    files = [f for f in listdir('./app/corpus') if isfile(join('./app/corpus', f)) and f[0] != '.']
    files_for_index = list()

    if BOOKS:
        for file in files:
            if file not in BOOKS:
                files_for_index.append(file)
    else:
        files_for_index = files

    with open('./src/files_to_index.txt', 'w') as file:
        for file_to_index in range(0, len(files_for_index) - 1):
            file.write(files_for_index[file_to_index])
            if file_to_index < len(files_for_index) - 2:
                file.write('\n')

    instance = IndexFileCreator(app.config['SELECTED_LANGUAGE'])
    instance.save_index()
    return render_template('update_index.html', instance=instance.get_unprocessed_files())


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file('./corpus/' + filename, attachment_filename=filename)


@app.route('/language/', defaults={'lang': 'es'})
@app.route('/language/<previous>/<lang>')
def language(previous, lang):
    if lang in app.config['LANGUAGES'] and app.config['SELECTED_LANGUAGE'] != lang:
        app.config['SELECTED_LANGUAGE'] = lang
        refresh()
    return redirect(url_for(previous))
