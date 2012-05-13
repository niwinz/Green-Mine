var StatsModel = Backbone.Model.extend({
    defaults: {
        'unassigned_points': 0,
        'assigned_points': 0,
        'total_points': 0,
        'percentage_completed': 0,
        'percentage_assigned': 0,
    },
    url: function() {
        return this.get('view').$el.attr('url');
    }
});

var BacklogStats = Backbone.View.extend({
    el: $(".user-story-stats"),

    initialize: function() {
        _.bindAll(this, 'render');
        this.model = new StatsModel({view:this});
    },

    render: function() {
        var self = this,
            deff = this.model.fetch();

        deff.done(function() {
            self.$el.html(self.model.get('stats_html'));
        });
    }
});

var Backlog = Backbone.View.extend({
    el: $("#dashboard"),

    initialize: function() {
        _.bindAll(this, 'render');
        
        this.stats_view = new BacklogStats();
        this.stats_view.render();
    },

    events: {
        "click .un-us-item .delete": "unassign_us",
        "dragstart .unassigned-us .un-us-item": "unassigned_us_dragstart",
        "dragover .milestones .milestone-item": "milestones_dragover",
        "dragleave .milestones .milestone-item": "milestones_drageleave",
        "drop .milestones .milestone-item": "milestones_on_drop",
        "dragstart .milestones .us-item": "milestones_dragstart",
        "dragover .left-block .unassigned-us": "left_block_dragover",
        "dragleave .left-block .unassigned-us": "left_block_dragleave",
        "drop .left-block .unassigned-us": "left_block_drop"
    },

    render: function() {},

    /* 
     * On click to delete button on unassigned user story list. 
    */
    unassign_us: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget);
        var buttons = {};
        buttons[gettext('Delete')] = function() {
            $(this).dialog('close');
            $.post(self.attr('href'), {}, function(data) {
                console.log(data);
                self.parents('.un-us-item').remove();
            });
        };

        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
        };

        $(".delete-us-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
    },

    unassigned_us_dragstart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy'; // only dropEffect='copy' will be dropable
        event.originalEvent.dataTransfer.setData('source_id', self.attr('id')); // required otherwise doesn't work
    },

    milestones_dragover: function(event) {
        event.originalEvent.dataTransfer.dropEffect = 'copy';
        event.preventDefault();

        var self = $(event.currentTarget);

        if (!self.hasClass("drag-over")) {
            self.addClass("drag-over");
        }
    },

    milestones_drageleave: function(event) {
        event.preventDefault();

        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
    },

    milestones_on_drop: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }

        var source_id = event.originalEvent.dataTransfer.getData('source_id');
        var source = $("#" + source_id);
        var assign_url = source.attr('assignurl');
        var milestone_id = self.attr('ref');

        $.post(assign_url, {mid: milestone_id}, function(data) {
            var data_object = $(data);
            self.find(".us-item-empty").remove()
            self.find(".milestone-userstorys").append(data_object);
            source.remove()
        }, 'html');

        // Refresh stats
        this.stats_view.render();
    },

    milestones_dragstart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy'; 
        event.originalEvent.dataTransfer.setData('source_id', self.attr('id'));
    },

    left_block_dragover: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.dropEffect = 'copy';
        event.preventDefault();
    },

    left_block_dragleave: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
        event.preventDefault();
    },

    left_block_drop: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
        
        var source_id = event.originalEvent.dataTransfer.getData('source_id');
        var source = $("#" + source_id);
        var unassign_url = source.attr('unassignurl');

        $.post(unassign_url, {}, function(data) {
            self.append(data);
            if(source.parent().find(".us-item").length == 1) {
                source.find(".us-meta").remove()
                source.find(".us-title").html(gettext("No user storys"));
                source.addClass('us-item-empty');
                source.attr('draggable', 'false');
                source.attr('unassignurl', '');
            } else {
                source.remove();
            }
        }, 'html');

        // Refresh stats
        this.stats_view.render();
    }
});

$(function() {
    var backlog = new Backlog();
});