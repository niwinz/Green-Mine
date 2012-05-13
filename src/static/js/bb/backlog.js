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

$(function() {
    var backlog_stats = new BacklogStats();
    backlog_stats.render();
});
