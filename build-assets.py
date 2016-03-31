from webassets import Bundle
from webassets import Environment


vendor_js = [
    "bower_components/jquery/dist/jquery.js",
    "bower_components/parsleyjs/dist/parsley.js",
    "bower_components/moment/moment.js",

    "bower_components/codemirror/lib/codemirror.js",
    "bower_components/codemirror/mode/markdown/markdown.js",
    "bower_components/codemirror/addon/mode/overlay.js",
    "bower_components/codemirror/mode/xml/xml.js",
    "bower_components/codemirror/mode/gfm/gfm.js",
    "bower_components/marked/lib/marked.js",

    "uikit-2.25.0/js/uikit.js",

    "uikit-2.25.0/js/components/accordion.js",
    "uikit-2.25.0/js/components/autocomplete.js",
    "uikit-2.25.0/js/components/datepicker.js",
    "uikit-2.25.0/js/components/form-password.js",
    "uikit-2.25.0/js/components/form-select.js",
    "uikit-2.25.0/js/components/grid-parallax.js",
    "uikit-2.25.0/js/components/grid.js",
    "uikit-2.25.0/js/components/htmleditor.js",
    "uikit-2.25.0/js/components/lightbox.js",
    "uikit-2.25.0/js/components/nestable.js",
    "uikit-2.25.0/js/components/notify.js",
    "uikit-2.25.0/js/components/pagination.js",
    "uikit-2.25.0/js/components/parallax.js",
    "uikit-2.25.0/js/components/search.js",
    "uikit-2.25.0/js/components/slider.js",
    "uikit-2.25.0/js/components/slideset.js",
    "uikit-2.25.0/js/components/slideshow.js",
    "uikit-2.25.0/js/components/slideshow-fx.js",
    "uikit-2.25.0/js/components/sortable.js",
    "uikit-2.25.0/js/components/sticky.js",
    "uikit-2.25.0/js/components/timepicker.js",
    "uikit-2.25.0/js/components/tooltip.js",
    "uikit-2.25.0/js/components/upload.js",]

vendor_css = [
    "uikit-2.25.0/css/uikit.almost-flat.css",

    "bower_components/codemirror/lib/codemirror.css",
    "uikit-2.25.0/css/components/accordion.almost-flat.css",
    "uikit-2.25.0/css/components/autocomplete.almost-flat.css",
    "uikit-2.25.0/css/components/datepicker.almost-flat.css",
    "uikit-2.25.0/css/components/dotnav.almost-flat.css",
    "uikit-2.25.0/css/components/form-advanced.almost-flat.css",
    "uikit-2.25.0/css/components/form-file.almost-flat.css",
    "uikit-2.25.0/css/components/form-password.almost-flat.css",
    "uikit-2.25.0/css/components/form-select.almost-flat.css",
    "uikit-2.25.0/css/components/htmleditor.almost-flat.css",
    "uikit-2.25.0/css/components/nestable.almost-flat.css",
    "uikit-2.25.0/css/components/notify.almost-flat.css",
    "uikit-2.25.0/css/components/placeholder.almost-flat.css",
    "uikit-2.25.0/css/components/progress.almost-flat.css",
    "uikit-2.25.0/css/components/search.almost-flat.css",
    "uikit-2.25.0/css/components/slidenav.almost-flat.css",
    "uikit-2.25.0/css/components/slider.almost-flat.css",
    "uikit-2.25.0/css/components/slideshow.almost-flat.css",
    "uikit-2.25.0/css/components/sortable.almost-flat.css",
    "uikit-2.25.0/css/components/sticky.almost-flat.css",
    "uikit-2.25.0/css/components/tooltip.almost-flat.css",
    "uikit-2.25.0/css/components/upload.almost-flat.css",


]

def main():

    my_env = Environment(
        directory='static',
        url='/static')
    all_js = Bundle(
        Bundle(*vendor_js),
        Bundle('coffee/common.coffee', filters='coffeescript'),
        #filters='jsmin',
        output='all.js'
    )
    my_env.register('all_js', all_js)

    all_css = Bundle(
        Bundle(*vendor_css
               #filters='cssmin'
               ),
        output='all.css'
    )
    my_env.register('all_css', all_css)

    for js_url in my_env['all_js'].urls():
        print js_url

    for css_url in my_env['all_css'].urls():
        print css_url

main()
