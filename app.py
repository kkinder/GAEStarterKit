from flask import Flask

import config

app = Flask(__name__)
app.secret_key = config.SECRET_STRING
app.production = not config.DEVELOPMENT
app.debug = app.development = config.DEVELOPMENT
