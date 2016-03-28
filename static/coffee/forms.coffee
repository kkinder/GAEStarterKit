#
# Helper scripts for forms

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

$('.ajax-loader-trigger').each (index, element) =>
    $(element).click =>

        uri = $(element).attr('data-target-href')
        console.log(uri)
        $(element).prop('disabled', true)

        $.ajax
            url: uri
            cache: true,
            dataType: "json"
            error: (jqXHR, textStatus, errorThrown) =>
                $(element).prop('disabled', false)
                UIkit.notify({
                    message: 'Error loading data: ' + errorThrown,
                    status: 'danger',
                    pos: 'top-left'
                })
            success: (data, textStatus, jqXHR) =>
                $(element).closest('.generic-loader').find('.ajax-loader-target').append(data.content)

                if data.next_cursor_url
                    $(element).attr('data-target-href', data.next_cursor_url)
                    $(element).prop('disabled', false)
                else
                    $(element).hide()

        return false;
