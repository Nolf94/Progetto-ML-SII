$(document).ready(function () {

    // reset ranking values and initialize aggregators
    $("[id$='__preferences']").each(function () {
        prefix_id = $(this).attr("id");

        var ranking = [0, 1, 2];

        $children = $("#" + prefix_id + "_values").children($("input[id$='_val']"));
        $children.each(function () {
            $(this).val(ranking[$(this).attr("index")]);
        });
        $("#" + prefix_id + "_aggregate").val(ranking);
    });
});

$(".sortable").sortable({
    animation: 150,

    onMove: function (evt, originalEvent) {
        $dragged = $('#' + evt.dragged.id);
        $dragged.addClass("bg-success text-white");
    },

    onEnd: function (evt) {
        id = evt.item.id
        mtype = id.split('-')[0]
        $item = $("#" + id);
        $item.removeClass("bg-success").removeClass("text-white");

        var inputs = $("input[id^=" + mtype + "][id$=" + '_val');
        var new_ranking = Array(inputs.len).fill(0);
        inputs.each(function () {
            // swap values
            var el = $(this)
            if (el.val() == evt.oldIndex) {
                el.val(evt.newIndex)
            }
            else if (el.val() == evt.newIndex) {
                el.val(evt.oldIndex)
            }
            new_ranking[el.attr('index')] = parseInt(el.val());
        })
        // update aggregate
        console.log(mtype, new_ranking);
        $("#" + mtype + "__preferences_aggregate").val(new_ranking);
    },
});