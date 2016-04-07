"""
Dealing with internationalization
"""
import datetime

from flask.ext.babel import Babel
from flask import request
from flask_moment import Moment

from app import app
import config

##
## Internationalization
babel = Babel(app)
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(config.languages.keys())

moment = Moment(app)

@app.context_processor
def inject_locale():
    return dict(
        config=config,
        global_now=datetime.datetime.utcnow(),
        js_dateformat='YYYY-MM-DD',
        js_timeformat='HH:MM:SS',
        js_datetimeformat='YYYY-MM-DD HH:MM:SS'
    )

