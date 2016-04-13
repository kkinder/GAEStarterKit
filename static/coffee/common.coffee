##
## This file is combined with vendor assets and outputted to all.js in build-assets.py
##


camelize = (str) ->
    str.replace /(?:^\w|[A-Z]|\b\w|\s+)/g, (match, index) ->
        if +match == 0
            return ''
        # or if (/\s+/.test(match)) for white spaces
        if index == 0 then match.toLowerCase() else match.toUpperCase()



initDatetimePickers = ->
    #
    # Throughout the application, we need combined date+time pickers. This helps combine those controls into one. See its use specifically in
    # forms.html
    $('.from-uikit-pickers').each (index, element) =>
        element = $(element)
        id = element.attr('id')

        parts = element.val().split(' ')
        if parts[0]
            $('#' + id + '--uikit-datepicker').val(parts[0])
            if parts[1]
                $('#' + id + '--uikit-timepicker').val(parts[1])

        update = =>
            element.val($('#' + id + '--uikit-datepicker').val() + ' ' + $('#' + id + '--uikit-timepicker').val())

        $('#' + id + '--uikit-datepicker').change(update)
        $('#' + id + '--uikit-timepicker').change(update)

spinButton = (button) ->
    $(button).prop('disabled', true)
    $(button).attr('old-content', $(button).html())
    $(button).html('<i class="uk-icon-spinner uk-icon-spin"></i>')

unspinButton = (button) ->
    $(button).prop('disabled', false)
    $(button).html($(button).attr('old-content'))

initAjaxLoaders = ->
    #
    # Automates having an ajax "load more" button.
    $('.ajax-loader-trigger').each (index, element) =>
        $(element).click =>
            uri = $(element).attr('data-target-href')
            spinButton(element)

            $.ajax
                url: uri
                cache: true,
                dataType: "json"
                error: (jqXHR, textStatus, errorThrown) =>
                    unspinButton(element)

                    UIkit.notify({
                        message: 'Error loading data: ' + errorThrown,
                        status: 'danger',
                        pos: 'top-left'
                    })
                success: (data, textStatus, jqXHR) =>
                    unspinButton(element)

                    $(element).closest('.generic-loader').find('.ajax-loader-target').append(data.content)

                    if data.next_cursor_url
                        $(element).attr('data-target-href', data.next_cursor_url)
                        $(element).prop('disabled', false)
                    else
                        $(element).hide()

            return false;

        if $(element).attr('data-load') == 'auto'
            $(element).click()


class DataWidget
    #
    # Subclass this to auto-initialize instances based on tags with data-widget, or whatever trigger attribute you have in @collectorAttrib
    @collectorAttrib = 'data-widget'
    @instances = []

    constructor: (element, options) ->


    @collect: (class_) =>
        #
        # Classmethod (or whatever you want to call it) that sweeps the DOM and looks for elements with data-widget from @collectorAttrib
        self = this
        $('*[' + class_.collectorAttrib + ']').each (index, element) ->
            options = {}
            $.each element.attributes, (i, attrib) ->
                name = attrib.name
                value = attrib.value
                if name.lastIndexOf('data-', 0) == 0
                    name = name.replace(/-/g, ' ')
                    name = name.slice(5)

                    if name.lastIndexOf('enable', 0) == 0 and value == ''
                        value = true
                    if name.lastIndexOf('disable', 0) == 0 and value == ''
                        value = true
                    options[camelize(name)] = value
            element = $(element)
            widget = new class_(element, options)
            self.instances.push(widget)

class AjaxButton extends DataWidget
    @collectorAttrib = 'data-ajax-button'

    constructor: (element, options) ->
        super()

        @options = options
        @element = element

        @params = {}
        #
        # Extract ajax-param-whatnot, all of which become parameter for the onclick ajax call
        for optionName, optionValue of options
            if optionName.lastIndexOf('ajaxParam', 0) == 0
                @params[optionName.slice(9).toLowerCase()] = optionValue

        @originalText = $(@element).text()
        @element.click(@onClick)


    guiSending: =>
        #
        # Reflect the fact that sending is happening
        if (@options.sendingText)
            @element.text(@options.sendingText)
        @element.prop('disabled', true)

        if @options.successClass
            @element.removeClass(@options.successClass)
        if @options.failureClass
            @element.removeClass(@options.failureClass)

    guiFailed: =>
        @element.prop('disabled', false)
        if @options.failureClass
            @element.addClass(@options.failureClass)

        if (@options.failureText)
            @element.text(@options.failureText)
        else
            @element.text(@originalText)

    guiSuccess: =>
        if (@options.disableAfterSuccess)
            @element.prop('disabled', true)
        else
            @element.prop('disabled', false)
        if @options.successClass
            @element.addClass(@options.successClass)

        if (@options.successText)
            @element.text(@options.successText)
        else
            @element.text(@originalText)

        if (@options.enableSuccessReload)
            location.reload()


    onClick: =>
        @guiSending()

        if (@options.confirmText)
            UIkit.modal.confirm @options.confirmText, =>
                @sendPost()
        else
            @sendPost()

    sendPost: =>
        $.ajax
            url: @options.ajaxUrl
            data: @params
            method: "POST"
            cache: false
            dataType: "json"
            error: (jqXHR, textStatus, errorThrown) =>
                @guiFailed()
                UIkit.notify({
                    message: 'Error: ' + errorThrown,
                    status: 'danger',
                    pos: 'top-left'
                })
            success: (data, textStatus, jqXHR) =>
                @guiSuccess()



##
## Code from flask-moment converted into handy CoffeeScript
flask_moment_render = (elem) ->
    $(elem).text eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';')
    $(elem).removeClass('flask-moment').show()
    return

flask_moment_render_all = ->
    $('.flask-moment').each ->
        flask_moment_render this
        if $(this).data('refresh')
            ((elem, interval) ->
                setInterval (->
                    flask_moment_render elem
                    return
                ), interval
                return) this, $(this).data('refresh')
        return
    return
moment.locale 'en'


$ ->
    flask_moment_render_all()
    initDatetimePickers()
    initAjaxLoaders()
    AjaxButton.collect(AjaxButton)

    $('.render-markdown').each ->
        content = $(this).text()
        $(this).html(marked(content))

    $('.shadow-hack').each ->
        content = $(this).text()
        if this.createShadowRoot
            shadow = this.createShadowRoot()
        else
            shadow = this
        $(shadow).html(content)
