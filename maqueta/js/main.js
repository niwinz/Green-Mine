var backlog_handlers = function() {
    $(".un-us-item .delete").live('click', function(event) {
        event.preventDefault();
        var self = $(this);
        self.closest('.un-us-item').css('border', '1px solid red');
        
        var buttons = {};
        buttons[gettext('Ok')] = function() {
            $.post(self.attr('href'), {}, function(data) {
                
            });
                
            $(this).dialog('close');
            self.parents('.un-us-item').remove();
        };
        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
            self.closest('.un-us-item').css('border', '');
        };

        $(".delete-us-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });        
    });
    
    $(".unassigned-us").on("click", ".config-us-inline", function(event) {
        event.preventDefault();
        var elm = $(this);
        $.get(elm.attr('href'),  function(data) {
            elm.closest('.un-us-item').find('.form-inline').html(data).show();
        }, 'html');
    });
    
    $(".unassigned-us").on('click', '.user-story-inline-submit', function(event) {
        event.preventDefault();

        var elm = $(this);
        var form = elm.closest('form');

        $.post(form.attr('action'), form.serialize(), function(data) {
            if(data.valid) {
                var usitem = elm.closest('.un-us-item');
                usitem.find('.form-inline').hide();
                
                if (data.action == 'save') {
                    usitem.replaceWith(data.html);
                } else {
                    var ml_id = form.find("#id_milestone").val();
                    var milestone = $("#milestone-" + ml_id);
                    
                    // hide empty entries.
                    milestone.find(".us-item-empty").hide()
                    milestone.find(".milestone-userstorys").append(data.html);
                    usitem.remove();
                }
            } else {
                /* Print form errors */
                form.find('.errorlist').remove();
                jQuery.each(data.errors, function(index, value){
                    var ul = $(document.createElement('ul'))
                        .attr('class', 'errorlist');
                    
                    for(var i=0; i<value.length; i++){
                        $(document.createElement('li')).html(value[i]).appendTo(ul);
                    }
                    
                    form.find('[name='+index+']').before(ul);
                })    
            }
        }, 'json');        
    });
    
    $(".unassigned-us").on('click', '.user-story-inline-cancel', function(event) {
        event.preventDefault();
        $(this).closest('.un-us-item').find('.form-inline').hide();
    });    

    $(".us-item .unassign").live('click', function(event) {
        event.preventDefault();
        var self = $(this);
        var pself = self.parents('.us-item');

        var buttons = {};
        buttons[gettext("Unassign")] = function() {            
            $.post(pself.attr('unassignurl'), {}, function(data) {
                $(".unassigned-us").prepend(data);
                
                var milestone_item_dom = self.parents('.milestone-item');
                if (milestone_item_dom.find('.milestone-userstorys .us-item').length == 1) {
                    pself.find('.us-meta').remove()
                    pself.find('.us-title').html(gettext("No user storys"));
                    pself.addClass('us-item-empty');
                } else {
                    pself.remove();
                }
            }, 'html');

            $(this).dialog('close');
        };

        buttons[gettext("Delete")] = function() {
            self.parents('.us-item').remove();
            $(this).dialog('close');
        };

        $(".unassign-dialog").dialog({
            width: "220px",
            modal: true,
            resizable: false,
            buttons: buttons
        });
    });
    
    $(".milestone-item .milestone-title  a.delete").live('click', function(event){
        event.preventDefault();
        var self = $(this);
        // TODO: ajax call
        
        var buttons = {};
        buttons[gettext('Ok')] = function() {
            $(this).dialog('close');
            self.parents('.milestone-item').remove();
        };
        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
        };

        $(".delete-milestone-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
    });
    
    //assign user story to milestone    
    
    var lightbox = $("#lightbox-backlog").lightbox({
        fadeIn: false,
        fadeOut: false,                
        width: 300
    });
    
    var us = {};
    $(".milestone a").live('click', function(e) {
        us = $(this);
        e.preventDefault();
        lightbox.open();
    });       
    
    $("#lightbox-backlog a").click(function(e){            
        e.preventDefault();
        var ml = $(this).attr('rel');
        
        $.post($(this).attr('href'), {'iref': us.attr('rel')}, function(data) {
            var milestone = $("#milestone-"+ml);
            if($(milestone).find('.us-item-empty').length > 0){
                $(milestone).find('.milestone-userstorys').html(data);
            }else{   
                $(milestone).find('.milestone-userstorys').append(data);
            }
        }, 'html');                
        
        us.closest('.un-us-item').remove();
        lightbox.close();
    });    
};

var settings_handlers = function() {
    $(".colors-form").on("click", ".tag-color-item .tag-rm", function(event) {
        $(this).parents(".tag-color-item").remove();
        if ($(".selected-colors .tag-color-item").length == 0) {
            $(".selected-colors").hide();
        }
    });

    $(".colors-form").on("click", "input[type='button']", function(event) {
        var new_dom = $('<div />', {'class': 'tag-color-item'});
        var name_dom = $('<div />', {'class': 'tag-name'});
        var color_dom = $('<div />', {'class': 'tag-color'});
        var close_dom = $('<div />', {'class': 'tag-rm'}).html("x");

        var tagname = $(this).parent().prev().prev().find('select').val();
        var colorvalue = $(this).parent().prev().find('input').val();
        
        name_dom.html(tagname);
        color_dom.css('background-color', colorvalue);
        color_dom.attr('val', colorvalue);

        new_dom
            .append(name_dom)
            .append(color_dom)
            .append(close_dom);
        
        if (tagname.length > 0) {
            $(".selected-colors").append(new_dom);
            $(".selected-colors").show();
        }
    });

    $("#edit-project-settings .width100 input[type=submit]").click(function(event) {
        event.preventDefault();
        var data = {};
        if ($('.tag-color-item').length > 0) {
            $('.tag-color-item').each(function() {
                var name = $(this).find(".tag-name").html();
                var value = $(this).find(".tag-color").attr('val');
                data[name] = value;
            });
            $("input[name=colors_hidden]").val($.toJSON(data));
        }

        $(this).parents('form').submit();
    });
};

$(document).ready(function() {
    backlog_handlers();
    settings_handlers();
});
