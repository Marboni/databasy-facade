$(function () {
    var roleSwitchHandler = function () {
        var currentButton = $(this);

        if (currentButton.attr('disabled')) {
            return;
        }

        currentButton.attr('disabled', 'disabled');

        var currentButtonGroup = currentButton.parent();
        var currentRoleSwitcher = currentButtonGroup.parent();

        var progressIndicator = currentRoleSwitcher.find('.progressIndicator');
        var successIndicator = currentRoleSwitcher.find('.successIndicator');
        var errorIndicator = currentRoleSwitcher.find('.errorIndicator');

        successIndicator.hide();
        progressIndicator.show();

        var role = $(this).data('role');
        var modelId = $(this).data('modelid');
        var objId = $(this).data('objid');

        var roleSwitcherType = currentRoleSwitcher.data('type');
        var url;
        if (roleSwitcherType == 'member') {
            url = '/models/' + modelId + '/team/' + objId + '/'
        } else if (roleSwitcherType == 'invitation') {
            url = '/models/' + modelId + '/team/invitations/' + objId + '/'
        } else {
            throw new Error('Unknown role switcher type "' + roleSwitcherType + '".')
        }
        var request = $.ajax({
            url: url,
            type:'POST',
            data:{role:role}
        });

        request.done(function () {
            currentButtonGroup.find('button').removeClass('btn-info').removeClass('disabled').removeAttr('disabled');
            currentButton.addClass('btn-info').addClass('disabled').attr('disabled', 'disabled');

            progressIndicator.hide();
            successIndicator.show();
            successIndicator.fadeOut(1000);
        });
        request.fail(function () {
            currentButton.removeAttr('disabled');

            progressIndicator.hide();
            errorIndicator.show();
            errorIndicator.fadeOut(3000);
        });
    };

    $('#members').find('.roleSwitcher button').click(roleSwitchHandler);
    $('#invitations').find('.roleSwitcher button').click(roleSwitchHandler);
});