import os
from flask import render_template, redirect, flash, url_for, request
from flask_babel import refresh
from werkzeug.utils import secure_filename
from app import app
from app.forms import QueryForm, UploadDocumentForm
from app.__init__ import MODEL
from flask_babel import _

THEMES = MODEL.get_themes()


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
            flash('Consulta realizada: {} con los siguientes temas: {}'.format(form.query.data, form.theme.data))
            return redirect(url_for('results'))
        else:
            if errors:
                return render_template('search.html', form=form, model=THEMES, errors=errors)
            else:
                return '', 204

    return render_template('search.html', form=form, model=THEMES)


@app.route('/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')


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


@app.route('/language/', defaults={'lang': 'es'})
@app.route('/language/<previous>/<lang>')
def language(previous, lang):
    if lang in app.config['LANGUAGES'] and app.config['SELECTED_LANGUAGE'] != lang:
        app.config['SELECTED_LANGUAGE'] = lang
        refresh()
    return redirect(url_for(previous))
