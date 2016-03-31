from flask import Blueprint

blueprint = Blueprint('tenants', __name__, template_folder='templates')

import controllers
import models
