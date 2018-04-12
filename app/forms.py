from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired


class QueryForm(FlaskForm):
    my_choices = [('1', 'All'), ('2', 'Adventures'), ('3', 'Novels')]
    query = StringField('', validators=[DataRequired()], render_kw={"placeholder": "Enter your query"})
    theme = SelectMultipleField(choices=my_choices, id='theme')
    submit = SubmitField('Search')
