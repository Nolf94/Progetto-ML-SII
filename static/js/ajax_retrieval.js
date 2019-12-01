$('#js-begin').hide();
$('#js-begin2').hide();
$("#js-progress").show();
function doAjax(to_django) {
    $.ajax({
        type: "POST",
        url: $('#js-progress').attr('ajax_url'),
        dataType: 'json',
        async: true,
        data: to_django,
        success: function(from_django) {
            console.log(from_django);
            if (!from_django.retrieval_done) {
                $("#js-progress-text-mtype").text(from_django.mtype);
                $("#js-progress-text-done").hide();
                $("#js-progress-text-moreinfo").hide();
                var percent = (from_django.i * 100 / from_django.tot).toFixed(0) + '%';
                $("#js-progress-bar").children().text(percent).css('width', percent);
                $("#js-progress-bar").children().attr('aria-valuenow', from_django.i);
                if (!from_django.current) {
                    $("#js-progress-bar").children().attr('aria-valuemax', from_django.tot);
                }
                if (from_django.next) {
                    if (from_django.next.name) $("#js-progress-data").text(from_django.next.name);
                    else $("#js-progress-data").text(from_django.mtype + ": " + from_django.next);
                    doAjax({}); // RECURSIVE CALL
                } else {
                    // $("#js-progress-bar").children()
                    //     .toggleClass('progress-bar-animated')
                    //     .toggleClass('progress-bar-striped');
                    $("#js-progress-text-done").show();
                    $("#js-progress-text-moreinfo").show();
                    $("#js-progress-data").text('');
                    $("#js-progress-bar").children().text('0%').css('width', '0%');
                    $("#js-done").show("fast");
                    $("#js-done--" + from_django.mtype).show("slow");
                    $("#js-done--" + from_django.mtype + " > .numretrieved").text(from_django.retrieved_items.length);
                    console.log(from_django.mtype + ": DONE.");
                    doAjax({'next_mtype': true});
                }
            } else {
                $("#js-progress").hide("slow");
                $("#js-progress-text").text("Done.").next().children().toggleClass('spinner-border');
                $("#js-progress-data").hide();
                $("#js-continue").show("slow");
                
                if ($("#js-results").length) { // REDIRECT TO RESULTS VIEW
                    var results_url = $('#js-results').attr('results_url')
                    console.log("Redirecting to results view...")
                    // # TODO SHOW REDIRECT LOADER
                    setTimeout(() => {
                        window.location.pathname = results_url
                    }, 2000);
                }
            }
        }
    });
};
doAjax({})