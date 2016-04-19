var triggerRemoveMember, triggerResendLink;

triggerRemoveMember = function(memberId) {
  var name, onyes, options, question, target;
  target = $('remove-' + memberId);
  name = $(target).attr('data-membership-display-name');
  onyes = function() {
    return $.ajax({
      url: '/account/-remove-member/' + memberId + '/',
      method: "POST",
      cache: false,
      dataType: "json",
      error: (function(_this) {
        return function(jqXHR, textStatus, errorThrown) {
          return UIkit.notify({
            message: 'Error removing member: ' + errorThrown,
            status: 'danger'
          });
        };
      })(this),
      success: (function(_this) {
        return function(data, textStatus, jqXHR) {
          $('#member-item-' + memberId).css('text-decoration', 'line-through');
          $('#member-item-' + memberId).find('.uk-button').hide();
          return UIkit.notify({
            message: 'Member removed',
            status: 'success'
          });
        };
      })(this)
    });
  };
  question = 'Are you sure you want to remove ' + name + ' from account?';
  options = {
    labels: {
      Ok: "Remove User"
    }
  };
  return UIkit.modal.confirm(question, onyes, null, options);
};

triggerResendLink = function(memberId) {
  return $.ajax({
    url: '/account/-resend-invite-email/' + memberId + '/',
    method: "POST",
    cache: false,
    dataType: "json",
    error: (function(_this) {
      return function(jqXHR, textStatus, errorThrown) {
        return UIkit.notify({
          message: 'Error resending email: ' + errorThrown,
          status: 'danger'
        });
      };
    })(this),
    success: (function(_this) {
      return function(data, textStatus, jqXHR) {
        return UIkit.notify({
          message: 'Invitation email re-sent',
          status: 'success'
        });
      };
    })(this)
  });
};
