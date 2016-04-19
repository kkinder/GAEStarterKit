triggerRemoveMember = (memberId) ->
    target = $('remove-' + memberId)

    name = $(target).attr('data-membership-display-name')

    onyes = ->
        $.ajax
            url: '/account/-remove-member/' + memberId + '/'
            method: "POST"
            cache: false
            dataType: "json"
            error: (jqXHR, textStatus, errorThrown) =>
                UIkit.notify({
                    message: 'Error removing member: ' + errorThrown,
                    status: 'danger'
                })
            success: (data, textStatus, jqXHR) =>
                $('#member-item-' + memberId).css('text-decoration', 'line-through')
                $('#member-item-' + memberId).find('.uk-button').hide()
                UIkit.notify({
                    message: 'Member removed',
                    status: 'success'
                })

    question = 'Are you sure you want to remove ' + name + ' from account?'

    options = {
        labels:
            Ok: "Remove User"
    }

    UIkit.modal.confirm question, onyes, null, options

triggerResendLink = (memberId) ->
    $.ajax
        url: '/account/-resend-invite-email/' + memberId + '/'
        method: "POST"
        cache: false
        dataType: "json"
        error: (jqXHR, textStatus, errorThrown) =>
            UIkit.notify({
                message: 'Error resending email: ' + errorThrown,
                status: 'danger'
            })
        success: (data, textStatus, jqXHR) =>
            UIkit.notify({
                message: 'Invitation email re-sent',
                status: 'success'
            })
