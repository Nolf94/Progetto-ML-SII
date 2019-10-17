$( document ).ready(function() {
    // selected array aggregates checkbox values
    var selected = [];

    // read from last request and check all previously selected items
    pre_selected = $("#selected").val()
    if (pre_selected.length) {
        pre_selected = pre_selected.split(',')
        pre_selected.forEach(function(id) {
            $("input:checkbox#"+id).prop('checked', true);
        })
    }
    
    // load selected array with checked items
    $("input:checkbox").each(function () {
        if ($(this).is(":checked")) {
            id = $(this).attr('id');
            selected.push($(this).attr('id'));
            // $("label[for="+id+"]").addClass("active")
        }
    });
    console.log(selected);
    

    // update selected array when an item is checked or un-checked
    $('input:checkbox').change(function(){        
        id = $(this).attr('id');
        label = $("label[for="+this.id+"]")
        if($(this).is(":checked")) {
            selected.push(id);
            // label.addClass("active");
        } else {
            selected.splice(selected.indexOf(id), 1)
            // label.removeClass("active");
        }
        console.log(selected);
        $("#selected").val(selected);
    });
});
