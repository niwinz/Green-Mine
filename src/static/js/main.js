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
    settings_handlers();
    tasks_issues_handlers();
    user_story_handlers();
    wiki_handlers();
});
