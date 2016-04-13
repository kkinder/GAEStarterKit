$ ->
    $('.member-remove-button').click (event) ->
        name = $(event.target).attr('data-membership-display-name')
        id = $(event.target).attr('data-membership-id')

        onyes = ->
            console.log('foo')

        question = 'Are you sure you want to remove ' + name + ' from account?'

        options  = {
            labels:
                Ok: "Remove User"
        }

        UIkit.modal.confirm question, onyes, null, options
