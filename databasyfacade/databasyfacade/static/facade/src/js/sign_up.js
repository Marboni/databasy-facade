$(function() {
    var invitation_hex = $('#su_invitation_hex').val();
    if (invitation_hex.length > 0) {
        $('#su_email').attr('readonly', 'readonly')
    }
});