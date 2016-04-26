"""`appengine_config` gets loaded when starting a new application instance."""
import os.path

from google.appengine.ext import vendor
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))

##
## Enable ctypes on dev appserver so we get proper flask tracebacks. From http://jinja.pocoo.org/docs/dev/faq/#my-tracebacks-look-weird-what-s-happening
## and http://stackoverflow.com/questions/3086091/debug-jinja2-in-google-app-engine
PRODUCTION_MODE = not os.environ.get(
    'SERVER_SOFTWARE', 'Development').startswith('Development')
if not PRODUCTION_MODE:
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']

