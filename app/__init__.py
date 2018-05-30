from flask import Flask
from flask_babel import Babel

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)


@babel.localeselector
def get_locale():
    return app.config['SELECTED_LANGUAGE']


from app import routes, models, errors
from app.models import Model

global MODEL
MODEL = Model()
