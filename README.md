[![Build Status](https://travis-ci.org/kkinder/GAEStarterKit.svg?branch=master)](https://travis-ci.org/kkinder/GAEStarterKit)

DEPRECATION NOTICE
==================

I am no longer maintaining this library. Unfortunately, [ndb](https://cloud.google.com/appengine/docs/standard/python/ndb/) does not and likely never will support Python 3, which I consider a showstopper for any new projects. The Python 3 environment for Google App engine [has far less functionality](https://cloud.google.com/appengine/docs/standard/python3/python-differences) than the Python 2 environment, so much so that it no longer makes sense to use something like GAEStarterKit.

I recommend a development stack of [Starlette](https://www.starlette.io/) (perhaps with [FastAPI](https://fastapi.tiangolo.com) or [Python Responder](https://github.com/kennethreitz/responder)) and [Vue.js](https://vuejs.org/) as a front-end. I think for most true SaaS applications, the days of traditional server-side MVCs are dead.

Once again, **I DO NOT RECOMMEND USING GAESTARTERKIT FOR NEW PROJECTS** and I am no longer actively maintaining it, though I would consider pull requests and/or a new maintainer if one steps foward.

GAE Starter Kit
===============

GAE Starter Kit is a prepared repository that jumpstarts your Google App Engine project. Built on [Flask], right out of the gate, GAE Starter Kit gives you:

**Security and user management**

  * Authentication via [Google users api], email+password, or social login (Facebook, GitHub, etc) via [Authomatic].
  * Multi-tenancy built in.
  * CSRF Protection through [SeaSurf].
  * Handy method decorators for admin, tenant, or login required pages.

**CRUD, Generic Views, and Forms**

  * Built with [WTForms] and [WTForms-Appengine]. Easily show forms, fully rendered, and connected to ndb models, with no repated code.
  * Automatic client-side form validation via [Parsley.js].
  * Server-side form errors displayed in a friendly way.
  * Generic Views (inspired by [Django]'s) that get you started writing basic views quickly.
  * Automatic Admin GUI generation.

**Easier Email**

  * Log outbound emails and how they were delivered. Especially useful in development.

**Includes Useful Defaults**

  * Integrated [UIKit] is a flexible and good-looking HTML5 framework with genuinely useful features.
  * [Moment.js] and [Flask-moment] provide easy and good-looking client-wide time/date representation, especially with UIKit's built-in time/date pickers.
  * Notifications fully integrated with flasher come out of the box.

**Flexibility**

  * Includes Assets built through [webassets], but can easily be changed out.
  * Disable any parts you don't want, and most of the framework continues to work as expected.
  * Liberal licensing via [Apache License]


Using GAE Starter Kit
---------------------

1. Clone the repository.
2. Copy `sample-config.py` to `config.py` and edit it as needed.
3. Install dependencies in `lib` directory: `pip install -t lib -r requirements.txt`
4. Run `dev_appserver.py .`
5. Enjoy

For a sample app, check out the included (and very simple) `apps.simplecms` app, which is referenced in the `installed_apps` variable in `sample-config.py`.

Releases
--------
If you'd like to use a specific *release* of GAEStarterKit, check it out specifically. For example, to checkout version 0.2, use:

    git checkout tags/v0.2

Rebuilding Assets
-----------------

GAE Starter Kit comes out of the factory, so to speak, with the static dir fully built out. However, if you find yourself needing to change the static assets, install webassets and any filters you need, and run `build-assets.py`

    $ pip install webassets
    $ pip install jsmin
    $ pip install cssmin
    $ python build-assets.py

Tutorial
--------
Read the [basic tutorial](https://github.com/kkinder/GAEStarterKit/blob/master/docs/tutorial.md) on developing with GAE Starter Kit.


License and Atribution
----------------------

GAE Starter Kit is by Ken Kinder <ken@kkinder.com>. It is distributed under the Apache Public License v2. See LICENSE for details.

GAE Starter Kit includes code from the following Open Source projects:

* [Authomatic]
* [CoffeeScript]
* [Flask-Babel]
* [Flask-Login]
* [Flask-Moment]
* [Flask-Restful]
* [Flask-Seasurf]
* [Flask-WTF]
* [Flask]
* [jQuery]
* [Moment.js]
* [Parsley.js]
* [Python-Markdown]
* [pytz]
* [UIKit]
* [WebAssets]
* [WTforms-Appengine]
* [WTForms-Components]
* [WTforms]

Each of these components also likely include code from other Open Source projcts.

[Apache License]: http://www.apache.org/licenses/LICENSE-2.0
[authomatic]: http://peterhudec.github.io/authomatic/
[CoffeeScript]: http://coffeescript.org/
[django]: https://www.djangoproject.com/
[Flask-Babel]: https://pythonhosted.org/Flask-Babel/
[Flask-Login]: https://flask-login.readthedocs.org/
[Flask-moment]: https://pypi.python.org/pypi/Flask-Moment
[Flask-Restful]: http://flask-restful-cn.readthedocs.org/
[Flask-Seasurf]: http://flask-seasurf.readthedocs.org/
[Flask-WTF]: https://flask-wtf.readthedocs.org/
[Flask]: http://flask.pocoo.org/
[google users api]: https://cloud.google.com/appengine/docs/python/users/
[jQuery]: https://jquery.com/
[Moment.js]: http://momentjs.com
[Parsley.js]: http://parsleyjs.org/
[Python-Markdown]: https://github.com/waylan/Python-Markdown
[pytz]: https://launchpad.net/pytz
[SeaSurf]: https://flask-seasurf.readthedocs.org/
[Uikit]: http://getuikit.com
[webassets]: https://webassets.readthedocs.org/
[WTForms-Appengine]: https://github.com/wtforms/wtforms-appengine
[WTForms-Components]: https://wtforms-components.readthedocs.org/
[WTForms]: https://github.com/wtforms/wtforms
