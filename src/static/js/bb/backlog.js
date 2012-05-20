/* Backlog Stats */

var StatsModel = Backbone.Model.extend({
    url: function() {
        return this.get('view').$el.attr('url');
    }
});

var StatsView = Backbone.View.extend({
    el: $(".user-story-stats"),

    initialize: function() {
        _.bindAll(this, 'render', 'reload');
        this.model = new StatsModel({view:this});
        this.model.fetch({success:this.render});
    },

    reload: function() {
        this.model.fetch({success:this.render});
    },

    render: function() {
        this.$el.html(this.model.get('stats_html'));
    }
});

/* Burndown */


var BurndownModel = Backbone.Model.extend({
    url: function() {
        return this.get('view').$el.attr('url');
    }
});

var BurndownView = Backbone.View.extend({
    el: $("#burndown"),

    initialize: function() {
        _.bindAll(this, 'render', 'reload');
        this.model = new BurndownModel({'view':this});
        this.model.fetch({success:this.render});
    },

    reload: function() {
        this.model.fetch({success:this.render});
    },

    render: function() {
        if (this.$el.attr('show') !== 'on') {
            return;
        }

        this.$("#burndown-graph").show();

        var d1 = new Array(),
            d2 = new Array(),
            d3 = new Array(),
            ticks = new Array();

        var total_points = this.model.get('total_points');
        var points_for_sprint = this.model.get('points_for_sprint');
        var sprints = this.model.get('sprints_number');
        var disponibility = this.model.get('disponibility');

        for(var i=0; i<=sprints; i++) {
            d1.push([i+1, total_points - points_for_sprint[i]]);
            d2.push([i+1, total_points - ((total_points/sprints)*i)]);
            d3.push([i+1, disponibility[i]]);
            ticks.push([i,"Sprint "+i])
        }

        $.plot(this.$('#burndown-graph'), [
            {
                data: d1,
                lines: { show: true, fill: true },
                points: { show: true }
            },
            {
                data: d2,
                lines: { show: true, fill: true },
                points: { show: true }
            },
            {
                data: d3,
                bars: { show: true }
            }
        ], { xaxis: { ticks: ticks } });
    }
});

/* Unassigned user storyes (left block) */

var LeftBlockModel = Backbone.Model.extend({
    url: function() {
        return this.get('view').fetch_url();
    }
});

var LeftBlockView = Backbone.View.extend({
    el: $(".left-block"),

    events: {
        "dragstart .unassigned-us .un-us-item": "unassigned_us_dragstart",
        "dragover .left-block .unassigned-us": "left_block_dragover",
        "dragleave .left-block .unassigned-us": "left_block_dragleave",
        "drop .left-block .unassigned-us": "left_block_drop",

        /* Iniline edit */
        "click .unassigned-us .config-us-inline": "on_us_edit_inline",
        "click .unassigned-us .user-story-inline-submit": "on_us_edit_inline_submit",
        "click .unassigned-us .user-story-inline-cancel": "on_us_edit_form_cancel",

        "click .un-us-item .delete": "onUserStoryDeleteClick",

        /* Ordering */
        "click .unassigned-us .head-title .row a": "on_order_link_clicked",
    },

    initialize: function() {
        _.bindAll(this, 'render', 'reload', 'fetch_url', 'onUserStoryDeleteClick');

        this.options.order_by = "-priority";

        this.model = new LeftBlockModel({view:this});
        this.model.on('change', this.render);
        this.model.fetch();
    },

    render: function() {
        this.$('.unassigned-us').html(this.model.get('html'))
    },

    fetch_url: function() {
        var base_url = this.$el.attr('url');
        return base_url + "?order_by=" + this.options.order_by;
    },

    /*
     * Reload state fetching new content from server. 
    */

    reload: function() {    
        this.model.fetch({success:this.render});
    },

    on_order_link_clicked: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget);
        
        var order_by = self.attr('order_by');
        var opt_key = "backlog_order_by_" + order_by + "_opt";
        var opt = localStorage.getItem(opt_key)

        if (opt == "" || opt === null) {
            this.options.order_by = order_by;
            localStorage.setItem(opt_key, "-")
        } else {
            this.options.order_by = "-" + order_by;
            localStorage.setItem(opt_key, "");
        }

        this.model.fetch({success:this.render});
    },


    /* 
     * On click to delete button on unassigned user story list. 
    */

    onUserStoryDeleteClick: function(event) {
        event.preventDefault();
        
        var self = $(event.currentTarget);
        var $this = this;
        var buttons = {};

        buttons[gettext('Delete')] = function() {
            $(this).dialog('close');
            $.post(self.attr('href'), {}, function(data) {
                self.parents('.un-us-item').remove();
                $this.reloadDependents();
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

    left_block_drop: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
        
        var source_id = event.originalEvent.dataTransfer.getData('source_id');
        var source = $("#" + source_id);
        var unassign_url = source.attr('unassignurl');
        var stats_view = this.options.stats_view;

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

            // Refresh stats
            stats_view.reload();
        }, 'html');

    },
    
    left_block_dragleave: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
        event.preventDefault();
    },
    
    left_block_dragover: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.dropEffect = 'copy';
        event.preventDefault();
    },

    unassigned_us_dragstart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy'; // only dropEffect='copy' will be dropable
        event.originalEvent.dataTransfer.setData('source_id', self.attr('id')); // required otherwise doesn't work
    },

    /*
     * On request visualize a inline edit user story form.
    */

    on_us_edit_inline: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget);
        $.get(self.attr('href'), function(data) {
            self.closest('.un-us-item').find('.form-inline').html(data).show();
        }, 'html');
    },

    /*
     * On inline user story edit form submit changes
    */

    on_us_edit_inline_submit: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget),
            form = self.closest('form'),
            stats_view = this.options.stats_view,
            $this = this;

        $.post(form.attr('action'), form.serialize(), function(data) {
            if (data.valid) {
                var usitem = self.closest('.un-us-item');
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
                form.find('.errorlist').remove();
                $.each(data.errors, function(index, value) {
                    var ul = $(document.createElement('ul'))
                        .attr('class', 'errorlist');
                    for(var i=0; i<value.length; i++){
                        $(document.createElement('li')).html(value[i]).appendTo(ul);
                    }
                    
                    form.find('[name='+index+']').before(ul);
                });
            }

            $this.reloadDependents();
        }, 'json');

    },

    reloadDependents: function() {
        this.options.stats_view.render();
        this.options.burndown_view.reload();
    },

    on_us_edit_form_cancel: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget);
        self.closest('.un-us-item').find('.form-inline').hide();
    },
});


/* Milestones (right block) */

var MilestonesModel = Backbone.Model.extend({
    url: function() {
        return this.get('view').$el.attr('url');
    }
});

var RightBlockView = Backbone.View.extend({
    el: $(".right-block"),

    events: {
        "dragover .milestones .milestone-item": "milestones_dragover",
        "dragleave .milestones .milestone-item": "milestones_drageleave",
        "drop .milestones .milestone-item": "milestones_on_drop",
        "dragstart .milestones .us-item": "milestones_dragstart",

        /* Milestone delete */
        "click .milestone-item .milestone-title a.delete": "on_milestone_delete_click"
    },

    initialize: function() {
        _.bindAll(this, 'render');
        this.model = new MilestonesModel({view:this});
        this.model.on('change', this.render);
        this.model.fetch();
    },

    render: function() {
        var self = this;
        self.$(".milestones").html(this.model.get('html'));
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
        var stats_view = this.options.stats_view;

        $.post(assign_url, {mid: milestone_id}, function(data) {
            var data_object = $(data);
            self.find(".us-item-empty").remove()
            self.find(".milestone-userstorys").append(data_object);
            source.remove()
            stats_view.render();
        }, 'html');
    },

    milestones_dragstart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy'; 
        event.originalEvent.dataTransfer.setData('source_id', self.attr('id'));
    },

    on_milestone_delete_click: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget), 
            buttons = {}, 
            left_block = this.options.parent.left_block,
            stats_view = this.options.stats_view;
        
    
        var buttons = {};
        buttons[gettext('Delete')] = function() {
            $(this).dialog('close');
            $.post(self.attr('href'), {}, function(data) {
                if (data.valid) {
                    self.parents('.milestone-item').remove();
                }
                stats_view.render();
                left_block.reload();
            }, 'json');
        };

        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close'); 
        };

        $(".delete-milestone-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
    }
});

var Backlog = Backbone.View.extend({
    el: $("#dashboard"),

    initialize: function() {
        _.bindAll(this, 'render');
        
        var stats_view = new StatsView();
        stats_view.render();

        var burndown_view = new BurndownView();

        this.left_block = new LeftBlockView({
            stats_view:stats_view, 
            burndown_view: burndown_view,
            parent:this
        });
        this.right_block = new RightBlockView({stats_view:stats_view, parent:this});
    },

    render: function() {},
});

$(function() {
    var backlog = new Backlog();
});
