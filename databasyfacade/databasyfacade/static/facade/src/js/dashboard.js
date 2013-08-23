$(function() {
    $('.deleteModel').click(function() {
        var modelId = $(this).data('modelid');
        var schemaName = $(this).data('schemaname');

        $('#deleteModelSchema').text(schemaName);
        $('#deleteModelButton').data('modelid', modelId);
        $('#deleteModelDialog').modal();
    });

    $('#deleteModelButton').click(function() {
        var modelId = $(this).data('modelid');
        window.location.href = '/models/' + modelId + '/delete/';
    });


    $('.giveUp').click(function() {
        var modelId = $(this).data('modelid');
        var schemaName = $(this).data('schemaname');

        $('#giveUpModelSchema').text(schemaName);
        $('#giveUpModelButton').data('modelid', modelId);
        $('#giveUpModelDialog').modal();
    });

    $('#giveUpModelButton').click(function() {
        var modelId = $(this).data('modelid');
        window.location.href = '/models/' + modelId + '/team/give-up/';
    });
});