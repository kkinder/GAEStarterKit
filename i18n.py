"""
This module contains code dealing with internationalization.

When imported, it adds the babel configuration to the existing flask app.

When called directly, it updates the "pot" file
"""
if __name__ == '__main__':
    import subprocess, sys, os

    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    # noinspection Restricted_Python_calls
    subprocess.check_call('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .', shell=True)
    # noinspection Restricted_Python_calls
    subprocess.check_call('pybabel update -i messages.pot -d translations', shell=True)
    # noinspection Restricted_Python_calls
    subprocess.check_call('pybabel compile -d translations', shell=True)
    sys.exit(0)

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
