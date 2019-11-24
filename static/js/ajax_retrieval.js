$('#js-begin').hide();
$("#js-progress").show();
function doAjax(to_django) {
    $.ajax({
        type: "POST",
        url: $('#js-progress').attr('ajax_url'),
        dataType: 'json',
        async: true,
        data: to_django,
        success: function(from_django) {
            console.log(from_django)
            if (!from_django.done) {
                $("#js-progress-text-mtype").text(from_django.mtype);
                if (!from_django.current) {
                    $("#js-progress-bar").children().attr('aria-valuemax', from_django.tot);
                }
                $("#js-progress-bar").children().attr('aria-valuenow', from_django.i);
                var percent = (from_django.i * 100 / from_django.tot).toFixed(0) + '%'
                $("#js-progress-bar").children().text(percent).css('width', percent);
                if (from_django.next) {           
                    if (from_django.next.name) $("#js-progress-data").text(from_django.next.name)
                    else $("#js-progress-data").text(from_django.mtype + ": " + from_django.next)
                    doAjax(from_django); // RECURSIVE CALL
                } else {
                    // $("#js-progress-bar").children()
                    //     .toggleClass('progress-bar-animated')
                    //     .toggleClass('progress-bar-striped');
                    
                    $("#js-done").show("fast");
                    $("#js-done--" + from_django.mtype).show("slow");
                    $("#js-done--" + from_django.mtype + " > .numretrieved").text(from_django.retrieved_items.length);
                    console.log(from_django.mtype + ": DONE.")
                    doAjax({'next_mtype': true})
                }
            } else {
                $("#js-progress").hide("slow")
                $("#js-progress-text").text("Done.").next().children().toggleClass('spinner-border');
                $("#js-progress-data").hide();
                $("#js-continue").show("slow");
            }
        }
    });
};
doAjax({})