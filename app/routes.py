from flask import render_template, redirect, flash, url_for
from app import app
from app.forms import QueryForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Juanca'}
    documents = [
        {
            'document': {'nameFile': 'test.pdf'},
            'description': 'This is a test!'
        },
        {
            'document': {'nameFile': 'novel.txt'},
            'description': 'This novel was so cool!'
        }
    ]

    return render_template('index.html', title='TFG', user=user, documents=documents)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = QueryForm()

    if form.validate_on_submit():
        flash('Login requested for user {}, lista de filtros: {}'.format(
            form.query.data, form.theme.data))
        return redirect(url_for('results'))

    return render_template('search.html', form=form)


@app.route('/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')
