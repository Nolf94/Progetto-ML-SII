
function init_results(keys) {
    keys.forEach( k => {
        // console.log($('#eval-'+k))
    })

    $('#evaluation').trigger('reset');


    $(".sortable").sortable({
        animation: 150,

        onMove: function (evt, originalEvent) {         
            $dragged = $('#' + evt.dragged.id);
            $dragged.addClass("bg-success text-white");
            // evt.dragged; // dragged HTMLElement
            // evt.draggedRect; // DOMRect {left, top, right, bottom}
            // evt.related; // HTMLElement on which have guided
            // evt.relatedRect; // DOMRect
            // evt.willInsertAfter; // Boolean that is true if Sortable will insert drag element after target by default
            // originalEvent.clientY; // mouse position
            // return false; — for cancel
            // return -1; — insert before target
            // return 1; — insert after target
        },

        onEnd: function (evt) {
            $item = $('#' + evt.item.id);
            $item.removeClass("bg-success").removeClass("text-white");
            
            console.log(evt.oldIndex, evt.newIndex)
            
            var inputs = $('input[id^=' + evt.item.id.split('-')[0] + ']');
            console.log(inputs);
            inputs.each( function() {
                var el = $(this)
                if (el.val() == evt.oldIndex) {                
                    el.val(evt.newIndex)
                }
                else if (el.val() == evt.newIndex) {
                    el.val(evt.oldIndex)
                }
            })

            // evt.to;    // target list
            // evt.from;  // previous list
            // evt.oldIndex;  // element's old index within old parent
            // evt.newIndex;  // element's new index within new parent
            // evt.oldDraggableIndex; // element's old index within old parent, only counting draggable elements
            // evt.newDraggableIndex; // element's new index within new parent, only counting draggable elements
            // evt.clone // the clone element
            // evt.pullMode;  // when item is in another sortable: `"clone"` if cloning, `true` if moving
        },
    });
}
