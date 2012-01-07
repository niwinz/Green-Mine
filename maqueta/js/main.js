var backlog_handlers = function() {
    $(".un-us-item .delete").live('click', function(event) {
        event.preventDefault();
    });

    $(".us-item .unassign").live('click', function(event) {
        event.preventDefault();
        var self = $(this);
        var pself = self.parents('.us-item');

        var buttons = {};
        buttons[gettext("Unassign")] = function() {
            var meta_data = pself.find('.meta-data');
            var view_url = meta_data.attr('viewurl');
            var ref = meta_data.attr('ref');
            var priorityid = meta_data.attr('priorityid');
            var priority = meta_data.attr('priority');
            var points = meta_data.attr('points');

            var dom = $('#examples .un-us-item').clone();
            dom.find('.identify a').html(ref).attr('href', view_url);
            dom.find('.title a').html(pself.find('.us-title').html()).attr('href', view_url);
            dom.find('.points span').html(points);
            dom.find('.priority span').html(priority).attr('priorityid', priorityid);
            $(".unassigned-us").prepend(dom);

            var milestone_item_dom = self.parents('.milestone-item');
            if (milestone_item_dom.find('.milestone-userstorys .us-item').length == 1) {
                pself.find('.us-meta').remove()
                pself.find('.us-title').html(gettext("No user storys"));
                pself.addClass('us-item-empty');
            } else {
                pself.remove();
            }

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
};

$(document).ready(function() {
    backlog_handlers();
    $(".submit-row input").button()
});
