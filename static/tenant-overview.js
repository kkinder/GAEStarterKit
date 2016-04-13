$(function() {
  return $('.member-remove-button').click(function(event) {
    var id, name, onyes, options, question;
    name = $(event.target).attr('data-membership-display-name');
    id = $(event.target).attr('data-membership-id');
    onyes = function() {
      return console.log('foo');
    };
    question = 'Are you sure you want to remove ' + name + ' from account?';
    options = {
      labels: {
        Ok: "Remove User"
      }
    };
    return UIkit.modal.confirm(question, onyes, null, options);
  });
});
