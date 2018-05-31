from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from flask_wtf.file import FileField
from flask_babel import lazy_gettext as _l


class QueryForm(FlaskForm):
    query = StringField('', render_kw={"placeholder": _l("Introduzca su consulta")})
    theme = SelectMultipleField(id='submit-themes')
    submit = SubmitField(_l('Buscar'))


class UploadDocumentForm(FlaskForm):
    names = StringField('', render_kw={"disabled": '', "placeholder": _l("Aquí se verán los nombres de los archivos que se van a subir a la aplicación ")})
    theme = SelectMultipleField(id='submit-themes')
    upload_files = FileField('', id='upload_files', render_kw={"multiple": ""})
    submit = SubmitField(_l('Enviar archivos'))


class UpdateThemesForm(FlaskForm):
    theme = SelectMultipleField(id='submit-themes')
    submit = SubmitField(_l('Actualizar'))