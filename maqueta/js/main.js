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
        fadeIn: true,
        fadeOut: true,                
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

$(document).ready(function() {
    backlog_handlers();
    //$(".submit-row input").button()
});
