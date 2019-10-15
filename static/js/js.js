$( document ).ready(function() {
    // selected array aggregates checkbox values
    var selected = [];

    // pre-check previously checked inputs if form is invalid
    preload = $("#preload").text()
    if (preload) {
        ids = preload.split(',');
        ids.forEach(id => {
            $('input#'+id).attr('checked', true)
        });
   }

    // pre-populate selected array if page is refreshed
    $("input[type=checkbox]").each(function() {
        if (this.checked == true) {
            selected.push(this.id)
        }
    });

    // update selected array on click
    $("label").click(function () {
        if ($(this).data("selected")) {
            $(this).removeClass("selected");
            $(this).data("selected", false);
            selected = selected.filter(x => this.id!=x);
        } else {
            $(this).addClass("selected");
            $(this).data("selected", true);
            selected.push(this.id);
        }
        console.log(selected)
        $("#selected").val(selected);
    });
});
