var backlog_handlers = function() {
    /* End backlog drag and drop */

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
                    milestone.find(".us-item-empty").remove()
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
    
    // Milestone item (user story) delete callback
    $(".milestones").on("click", ".us-item .unassign", function(event) {
        event.preventDefault();
        var self = $(this);
        var pself = self.parents('.us-item');

        var buttons = {};
        buttons[gettext("Delete")] = function() {   
            // TODO: ajax call
            self.parents('.us-item').remove();
            $(this).dialog('close');
        };

        buttons[gettext("Cancel")] = function() {
            $(this).dialog('close');
        };

        $(".unassign-dialog").dialog({
            width: "220px",
            modal: true,
            resizable: false,
            buttons: buttons
        });
    });
    
    // Milestone delete callback
    $(".milestone-item .milestone-title  a.delete").live('click', function(event){
        event.preventDefault();
        var self = $(this);
        
        var buttons = {};
        buttons[gettext('Delete')] = function() {
            // TODO: ajax call
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
};

var settings_handlers = function() {
    $(".selected-colors").on("click", ".tag-color-item .tag-rm", function(event) {
        $(this).parents(".tag-color-item").remove();
        if ($(".selected-colors .tag-color-item").length == 0) {
            $(".selected-colors").hide();
        }
    });

    $(".colors-section").on("click", "input[type='button']", function(event) {
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

var tasks_issues_handlers = function() {
    $(".unassigned-us").on('click', '.un-us-item img.delete', function(event) {
        var self = $(this);
        var buttons = {};

        buttons[gettext('Delete')] = function() {
            var delete_url = self.attr('deleteurl');
            $.post(delete_url, {}, function(data) {
                if(data.valid) { 
                    self.parents('.un-us-item').remove();
                }
            }, 'json');
            $(this).dialog('close');
        };
        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
        };

        $(".delete-milestone-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
        event.preventDefault();
    });
};

var user_story_handlers = function() {
    $(".us-tasks-list").on("click", ".us-task-item img.delete", function(event) {
        var self = $(this);
        var buttons = {};

        buttons[gettext('Delete')] = function() {
            var delete_url = self.attr('deleteurl');
            $.post(delete_url, {}, function(data) {
                if(data.valid) { 
                    self.parents('.us-task-item').remove();
                }
            }, 'json');
            $(this).dialog('close');
        };
        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
        };

        $(".delete-task-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
        event.preventDefault();
    });
};

var wiki_handlers = function() {
    $("#wiki-module").on('click', '.show-menu', function(event) {
        event.preventDefault();
        
        var wiki_menu = $("#wiki-menu");
        if (wiki_menu.is(":hidden")) {
            wiki_menu.show();
        } else {
            wiki_menu.hide();
        }
    });
};

$(document).ready(function() {
    backlog_handlers();
    settings_handlers();
    tasks_issues_handlers();
    user_story_handlers();
    wiki_handlers();
});
