from __future__ import print_function

import os
import sys

#
# Verify webassets is installed
try:
    from webassets import Bundle
    from webassets import Environment
except ImportError:
    print("You just install webassets to build new assets.", file=sys.stderr)
    print("pip install webassets.", file=sys.stderr)
    sys.exit(1)

#
# Make sure we're in the project directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

#
# Verify CoffeeScript is installed
try:
    import webassets.filter.coffeescript
    from StringIO import StringIO

    test_filter = webassets.filter.coffeescript.CoffeeScript()
    input = StringIO('')
    output = StringIO()

    test_filter.output(input, output)
    print(output.getvalue())
except Exception as e:
    print('Unable to do CoffeeScript test. Is CoffeeScript installed?', file=sys.stderr)
    print('To install via npm: npm install -g coffee-script', file=sys.stderr)
    print('You must also have Node.js installed to use CoffeeScript. See: https://nodejs.org/en/download/', file=sys.stderr)
    print('', file=sys.stderr)
    print(e.message, file=sys.stderr)
    sys.exit(1)

vendor_js = [
    "bower_components/jquery/dist/jquery.js",
    "bower_components/parsleyjs/dist/parsley.js",
    "bower_components/moment/moment.js",
    "bower_components/js-cookie/src/js.cookie.js",

    "bower_components/codemirror/lib/codemirror.js",
    "bower_components/codemirror/mode/markdown/markdown.js",
    "bower_components/codemirror/addon/mode/overlay.js",
    "bower_components/codemirror/mode/xml/xml.js",
    "bower_components/codemirror/mode/gfm/gfm.js",
    "bower_components/marked/lib/marked.js",

    "uikit-2.27.1/js/uikit.js",

    "uikit-2.27.1/js/components/accordion.js",
    "uikit-2.27.1/js/components/autocomplete.js",
    "uikit-2.27.1/js/components/datepicker.js",
    "uikit-2.27.1/js/components/form-password.js",
    "uikit-2.27.1/js/components/form-select.js",
    "uikit-2.27.1/js/components/grid-parallax.js",
    "uikit-2.27.1/js/components/grid.js",
    "uikit-2.27.1/js/components/htmleditor.js",
    "uikit-2.27.1/js/components/lightbox.js",
    "uikit-2.27.1/js/components/nestable.js",
    "uikit-2.27.1/js/components/notify.js",
    "uikit-2.27.1/js/components/pagination.js",
    "uikit-2.27.1/js/components/parallax.js",
    "uikit-2.27.1/js/components/search.js",
    "uikit-2.27.1/js/components/slider.js",
    "uikit-2.27.1/js/components/slideset.js",
    "uikit-2.27.1/js/components/slideshow.js",
    "uikit-2.27.1/js/components/slideshow-fx.js",
    "uikit-2.27.1/js/components/sortable.js",
    "uikit-2.27.1/js/components/sticky.js",
    "uikit-2.27.1/js/components/timepicker.js",
    "uikit-2.27.1/js/components/tooltip.js",
    "uikit-2.27.1/js/components/upload.js", ]

uikit_theme_suffix = '.almost-flat'

vendor_css = [
    "uikit-2.27.1/css/uikit%s.css" % uikit_theme_suffix,

    "bower_components/codemirror/lib/codemirror.css",
    "uikit-2.27.1/css/components/accordion%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/autocomplete%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/datepicker%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/dotnav%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/form-advanced%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/form-file%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/form-password%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/form-select%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/htmleditor%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/nestable%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/notify%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/placeholder%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/progress%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/search%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/slidenav%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/slider%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/slideshow%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/sortable%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/sticky%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/tooltip%s.css" % uikit_theme_suffix,
    "uikit-2.27.1/css/components/upload%s.css" % uikit_theme_suffix,
]

for file in vendor_css + vendor_js:
    if not os.path.exists(os.path.join('static', file)):
        print('%s not found' % file, file=sys.stderr)
        sys.exit(1)


def main():
    my_env = Environment(
        directory='static',
        url='/static')

    #
    # The js for every pge
    all_js = Bundle(
        Bundle(*vendor_js),
        Bundle('coffee/common.coffee', filters='coffeescript'),
        # filters='jsmin',
        output='all.js'
    )
    my_env.register('all_js', all_js)

    #
    # Per-page coffee
    page_bundles = []
    for file in os.listdir(os.path.join(os.path.abspath('.'), 'static/coffee')):
        if file.endswith('.coffee') and not file.startswith('#') and file != 'common.coffee':
            bundle_name = file.split('.')[0]
            bundle = Bundle(os.path.join('coffee', file), filters='coffeescript', output='%s.js' % bundle_name)
            my_env.register(bundle_name, bundle)
            page_bundles.append(bundle_name)

    #
    # CSS for every page
    all_css = Bundle(
        Bundle(*vendor_css
               # filters='cssmin'
               ),
        output='all.css'
    )
    my_env.register('all_css', all_css)

    for js_url in my_env['all_js'].urls():
        print(js_url)

    for css_url in my_env['all_css'].urls():
        print(css_url)

    for page_bundle in page_bundles:
        for url in my_env[page_bundle].urls():
            print(url)


main()
