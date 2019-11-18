$('#js-connect').hide();
$("#js-progress").show();
function doAjax(to_django) {
    $.ajax({
        type: "POST",
        url: $('#js-progress').attr('ajax_url'),
        dataType: 'json',
        async: true,
        data: to_django,
        success: function(from_django) {
            if (!from_django.current) {
                $("#js-progress-bar").children().attr('aria-valuemax', from_django.tot);
            }
            $("#js-progress-bar").children().attr('aria-valuenow', from_django.i);
            var percent = (from_django.i * 100 / from_django.tot).toFixed(0) + '%'
            $("#js-progress-bar").children().text(percent).css('width', percent);
            $("#js-progress-data").text(from_django.next)
            if (from_django.next) { 
                doAjax(from_django); // RECURSIVE CALL
            } else {
                $("#js-progress-text").text("Done.").next().children().toggleClass('spinner-border');
                // $("#js-progress-bar").children()
                //     .toggleClass('progress-bar-animated')
                //     .toggleClass('progress-bar-striped');
                $("#js-progress").hide("slow")
                $("#js-progress-data").hide();
                $("#js-done").show("slow");
                $("#js-done-numretrieved").text(from_django.retrieved_items.length);
            }
        }
    });
};
doAjax({})