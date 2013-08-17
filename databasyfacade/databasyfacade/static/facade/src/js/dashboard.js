$(function() {
    $('.deleteModel').click(function() {
        var modelId = $(this).data('modelid');
        var schemaName = $(this).data('schemaname');

        $('#deleteModelId').text(schemaName);
        $('#deleteModelButton').data('modelid', modelId);
        $('#deleteModelDialog').modal();
    });

    $('#deleteModelButton').click(function() {
        var modelId = $(this).data('modelid');
        window.location.href = '/models/' + modelId + '/delete/';
    });
});