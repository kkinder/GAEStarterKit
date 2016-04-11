"""
Users blueprint/app handles logging users out, using Authomatic for federated logins, resetting passwords, a user profile page, and multi-tenancy. Oh my!
"""
import config
from flask import Blueprint, session, redirect, url_for

blueprint = Blueprint('users', __name__,
                      template_folder='templates')

import controllers
import models
import system

from app import app


app.register_blueprint(blueprint)
