/* Models */

Greenmine.Models.Tag = Backbone.Model.extend({});
Greenmine.Models.UserStory = Backbone.Model.extend({});
Greenmine.Models.Milestone = Backbone.Model.extend({
    userStoriesCollection: Backbone.Collection.extend({
        model: Greenmine.Models.UserStory
    }),
    initialize: function() {
        this.userStories = new this.userStoriesCollection(this.get('userStories'));
    }
});


/* Collections */

Greenmine.Collections.Tags = Backbone.Collection.extend({
    model: Greenmine.Models.Tag
});

Greenmine.Collections.UnassignedUserstories = Backbone.Collection.extend({
    model: Greenmine.Models.UserStory
});

Greenmine.Collections.Milestones = Backbone.Collection.extend({
    model: Greenmine.Models.Milestone
});

Greenmine.Collections.milestones = new Greenmine.Collections.Milestones();
Greenmine.Collections.unassignedUserstories = new Greenmine.Collections.UnassignedUserstories();
Greenmine.Collections.tags = new Greenmine.Collections.Tags();


/* Templates */

Greenmine.Templates.tag = Handlebars.compile($("#filter-template").html());
Greenmine.Templates.milestone = Handlebars.compile($("#milestone-template").html());
Greenmine.Templates.unassignedUserstory = Handlebars.compile($("#unassigned-us-template").html());
Greenmine.Templates.assignedUserstory = Handlebars.compile($("#assigned-us-template").html());


/* Views */

Greenmine.Views.TagView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "tag"
    },
    render: function() {
        this.$el.html(Greenmine.Templates.tag(this.model.toJSON()));
        return this;
    }
});

Greenmine.Views.UserStory = Backbone.View.extend({
    tagName: "div",

    attributes: {
        "class": "list-item",
        "draggable": "true"
    },

    initialize: function() {
        _.bindAll(this);
        this.$el.attr('data-id', this.model.get('id'));
        this.$el.attr('id', 'user-story-' + this.model.get('id'));
        this.$el.data('view', this);
    },

    setAssigned: function(value) {
        this.options.assigned = value;
    },

    render: function() {
        if (this.options.assigned === undefined || this.options.assigned === false) {
            this.$el.html(Greenmine.Templates.unassignedUserstory(this.model.toJSON()));
        } else {
            this.$el.html(Greenmine.Templates.assignedUserstory(this.model.toJSON()));
        }

        return this;
    }
});

Greenmine.Views.Milestone = Backbone.View.extend({
    tagName: "div",
    attributes: {
        "class": "milestone-item"
    },

    initialize: function() {
        _.bindAll(this);

        this.$el.attr('id', 'milestone-' + this.model.get('id'));
        this.$el.data('view', this);
        this.model.userStories.on("add", this.renderUserStory);
    },

    renderUserStory: function(item) {
        var view = new Greenmine.Views.UserStory({model:item, assigned: true})
        this.$(".milestone-userstorys").append(view.render().el);
    },

    render: function() {
        this.$el.html(Greenmine.Templates.milestone(this.model.toJSON()));
        this.model.userStories.each(this.renderUserStory);
        return this;
    }
});

Greenmine.Views.GraphsView = Backbone.View.extend({
    el: "#graphs",

    initialize: function() {
        _.bindAll(this);
        this.burnup = this.$("#burnup");
        this.burndown = this.$("#burndown");
        this.reloadAll();
    },

    reloadAll: function() {
        this.reloadBurnup();
        this.reloadBurndown();
    },

    reloadBurnup: function() {
        if (this.burnup.data('show') == 'on') {
            var self = this;
            $.get(this.$el.data('burnup-api-url'), function(data) {
                self.renderBurnup(new Backbone.Model(data));
            }, 'json');
        }
    },

    reloadBurndown: function() {
        if (this.burndown.data('show') == 'on') {
            var self = this;
            $.get(this.$el.data('burndown-api-url'), function(data) {
                self.renderBurndown(new Backbone.Model(data));
            }, 'json');
        }
    },

    renderBurnup: function(model) {
        this.burnup.find("#burnup-graph").show();

        var d1 = new Array(),
            d2 = new Array(),
            d3 = new Array(),
            d4 = new Array(),
            ticks = new Array();

        var sprints = model.get('sprints');
        var total_points = model.get('total_points');
        var total_sprints = model.get('total_sprints');
        var now_position = model.get('now_position');

        Ticks.push([1,"Kickoff"]);
        for(var i=0; i<=total_sprints; i++) {
            d1.push([i+1, total_points]);

            if(now_position && (sprints[0][i+1]==null)) {
                d2.push([now_position, sprints[0][i]]);
            } else {
                d2.push([i+1, sprints[0][i]]);
            }

            if(now_position && (sprints[1][i+1]==null)) {
                d3.push([now_position, sprints[1][i]]);
            } else {
                d3.push([i+1, sprints[1][i]]);
            }

            if(now_position && (sprints[2][i+1]==null)) {
                d4.push([now_position, sprints[2][i]]);
            } else {
                d4.push([i+1, sprints[2][i]]);
            }
            ticks.push([i+2,"Sprint "+(i+1)]);
        }

        var max_extra_points = _.reduce(d4, function(memo, num){
            if(num[1] != undefined) {
                return Math.max(memo, num[1]);
            } else {
                return memo;
            }
        }, 0);

        max_extra_points += _.reduce(d3, function(memo, num){
            if(num[1] != undefined) {
                return Math.max(memo, num[1]);
            } else {
                return memo;
            }
        }, 0);

        $.plot($("#burnup-graph"), [
            {
                data: d1,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#eec446',
                stack: 'other_bars'
            },
            {
                data: d3,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#ff77ff',
                stack: 'other_bars'
            },
            {
                data: d4,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#cb4b4b',
                stack: 'other_bars'
            },
            {
                data: d2,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#669900',
                stack: 'greengraph'
            },
            {
                data: [[now_position, 0], [now_position, total_points+max_extra_points+5]],
                lines: { show: true, fill: true },
                points: { show: false },
                color: "#888888",
                stack: 'bar'
            }
        ], {
            series: {
                stack: true,
                lines: { show: true, fill: true, steps: false },
                bars: { show: false, barWidth: 0.6 }
            },
            xaxis: { ticks: ticks },
            yaxis: { position: "right", labelWidth: 40 },
            grid: { borderWidth: 0},
        });
    },

    renderBurndown: function(model) {
        this.burndown.find("#burndown-graph").show();

        var d1 = new Array(),
            d2 = new Array(),
            d3 = new Array(),
            d4 = new Array(),
            ticks = new Array();

        var total_points = model.get('total_points');
        var points_for_sprint = model.get('points_for_sprint');
        var sprints = model.get('sprints_number');
        var extra_points = model.get('extra_points');
        var now_position = model.get('now_position');

        ticks.push([1,"Kickoff"]);
        for(var i=0; i<=sprints; i++) {
            if(now_position && (points_for_sprint[i+1]==null)) {
                d1.push([now_position, total_points - points_for_sprint[i]]);
            } else {
                d1.push([i+1, total_points - points_for_sprint[i]]);
            }
            d2.push([i+1, total_points - ((total_points/sprints)*i)]);
            if(now_position && (extra_points[i+1]==null)) {
                d3.push([now_position, -extra_points[i]]);
            } else {
                d3.push([i+1, -extra_points[i]]);
            }
            ticks.push([i+2,"Sprint "+(i+1)])
        }

        var min_extra_points = _.reduce(d3, function(memo, num){
            if(num[1]) {
                return Math.min(memo, num[1]);
            } else {
                return memo;
            }
        }, 0);

        $.plot(this.burndown.find('#burndown-graph'), [
            {
                data: d2,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#eec446'
            },
            {
                data: d1,
                lines: { show: true, fill: false },
                points: { show: true },
                color: '#669900'
            },
            {
                data: d3,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#cb4b4b'
            },
            {
                data: [[now_position, min_extra_points-5], [now_position, total_points+5]],
                lines: { show: true, fill: true },
                points: { show: false },
                color: "#888888",
            }
        ],
        {
            xaxis: { ticks: ticks },
            yaxis: { position: "right", labelWidth: 40 },
            grid: { borderWidth: 0 }
        });
    }
});


Greenmine.Views.StatsView = Backbone.View.extend({
    el: "#stats",

    initialize: function() {
        _.bindAll(this);
    },

    reload: function() {
        $.get(this.$el.data('stats-api-url'), this.reloadSuccess, 'json');
    },

    reloadSuccess: function(data) {
        this.renderStats(new Backbone.Model(data));
    },

    renderStats: function(model) {
        this.$("progress").val(model.get('percentage_completed'));
        this.$("#completed-points .info-text-main span").html(model.get('percentage_completed'));
        this.$("#total-points .info-text-main").html(model.get("total_points"));
        this.$("#assigned-points .info-text-main").html(model.get("assigned_points"));
    }
});


Greenmine.Views.Backlog = Backbone.View.extend({
    el: "#backlog",

    events: {
        "click .milestones-form .create": "submitMilestone",
        "click .milestones-form .cancel": "hideMilestoneForm",
        "click .milestones-header .show-milestone-form": "showMilestoneForm",

        "click .show-hide-graphics a": "toggleGraphsVisibility",
        "click #show-userstory-form": "toggleUserstoryFormVisibility",
        "click .userstory-form .plus": "addAdditionalUserstoryInput",

        "drop .milestones .milestone-item": "onDropToMilestones",
        "drop .uslist-box": "onDropToUnassigned",
        "dragstart .uslist-box .list-item": "dragStart",
        "dragstart .milestones-list .list-item": "dragStart",

        "dragend .uslist-box .list-item": "dragEnd",
        "dragend .milestones-list .list-item": "dragEnd",

        "dragover .uslist-box": "onUnassginedDragover",
        "dragover .milestones .milestone-item": "onMilestonesDragover",

        "dragenter .milestones .milestone-item": "onMilestonesDragenter",
        "dragenter .uslist-box": "onUnassginedDragenter",

        "dragleave .milestones .milestone-item": "onMilestonesDragleave",
        "dragleave .uslist-box": "onUnassginedDragleave",
    },

    dragEffect: "move",
    dragEffectAllowed: "move",

    initialize: function() {
        _.bindAll(this);

        Greenmine.Views.graphs = new Greenmine.Views.GraphsView();
        Greenmine.Views.stats = new Greenmine.Views.StatsView();

        Greenmine.Collections.milestones.on("reset", this.resetMilestones);
        Greenmine.Collections.unassignedUserstories.on("reset", this.resetUnassingedUserStories);
    },

    dragStart: function(event) {
        //event.originalEvent.dataTransfer.effectAllowed = 'copy'
        var target = $(event.currentTarget);
        target.css('opacity', '0.4');
        event.originalEvent.dataTransfer.effectAllowed = this.dragEffectAllowed;
        event.originalEvent.dataTransfer.setData('source', "#" + target.attr('id'));

    },

    dragEnd: function(event) {
        var target = $(event.currentTarget);
        target.css('opacity', '1.0');
    },

    onUnassginedDragover: function(event) {
        if (event.preventDefault) { event.preventDefault(); }
        event.originalEvent.dataTransfer.dropEffect = this.dragEffect;
        return false;
    },

    onUnassginedDragenter: function(event) {
        event.originalEvent.dataTransfer.effectAllowed = 'move'
        var target = $(event.currentTarget);
        target.addClass('over');
    },

    onUnassginedDragleave: function(event) {
        var target = $(event.currentTarget);
        target.removeClass('over');
    },

    onMilestonesDragover: function(event) {
        if (event.preventDefault) { event.preventDefault(); }
        event.originalEvent.dataTransfer.dropEffect = this.dragEffect;
        return false;
    },

    onMilestonesDragenter: function(event) {
        var target = $(event.currentTarget);
        target.addClass('over');
    },

    onMilestonesDragleave: function(event) {
        var target = $(event.currentTarget);
        target.removeClass('over');
    },

    onDropToMilestones: function(event) {
        event.originalEvent.dataTransfer.dropEffect = this.dragEffect;
        event.stopPropagation();

        var sourceId, view, target;

        sourceId = event.originalEvent.dataTransfer.getData('source');
        view = this.$(sourceId).data('view');
        view.setAssigned(true);

        target = $(event.currentTarget);
        target.find(".milestone-userstorys").append(view.render().el);

        sourceId = view = target = null;
    },

    onDropToUnassigned: function(event) {
        event.originalEvent.dataTransfer.dropEffect = this.dragEffect;
        event.stopPropagation();

        var sourceId, view, target;

        sourceId = event.originalEvent.dataTransfer.getData('source');
        view = this.$(sourceId).data('view');
        view.setAssigned(false);

        target = $(event.currentTarget);
        target.find(".list-body").append(view.render().el);

        sourceId = view = target = null;
    },

    addAdditionalUserstoryInput: function(event) {
        event.preventDefault();

        var templateDom = this.$(".userstory-form .template-row").clone()
        templateDom.find("textarea").val("");
        templateDom.removeClass("template-row");
        this.$(".userstory-form .form-items").append(templateDom);
    },

    toggleUserstoryFormVisibility: function(event) {
        event.preventDefault();
        var userstoryForm = this.$(".userstory-form");

        if (userstoryForm.hasClass("hidden")) {
            userstoryForm.removeClass("hidden");
        } else {
            userstoryForm.addClass("hidden");
            var templateDom = this.$(".userstory-form .template-row").clone()
            templateDom.find("textarea").val("");

            this.$(".userstory-form .form-items").empty();
            this.$(".userstory-form .form-items").html(templateDom)

        }
    },

    /* Display or hide graphs block */

    toggleGraphsVisibility: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        var graphs = this.$("#graphs");

        if (graphs.hasClass("hidden")) {
            graphs.removeClass("hidden");
            target.html(gettext("Hide graphics"));
        } else {
            graphs.addClass("hidden");
            target.html(gettext("Show graphics"));
        }
    },

    submitMilestone: function(event) {
        event.preventDefault();
    },

    hideMilestoneForm: function(event) {
        event.preventDefault();
        this.$(".milestones-form").addClass("hidden");
    },

    showMilestoneForm: function(event) {
        event.preventDefault();
        this.$(".milestones-form").removeClass("hidden");
    },

    reloadMilestones: function() {
        $.get(this.$("#milestones").data('api-url'), this.reloadMilestonesSuccess, 'json');
    },

    reloadMilestonesSuccess: function(data) {
        Greenmine.Collections.milestones.reset(data.milestones);
    },

    reloadUnassigned: function() {
        $.get(this.$(".uslist-box").data('url'), this.reloadUnassignedSuccess, 'json');
    },

    reloadUnassignedSuccess: function(data) {
        Greenmine.Collections.unassignedUserstories.reset(data.unassigned_us);
    },

    resetMilestones: function() {
        var self = this;
        this.$("#milestones").empty();

        Greenmine.Collections.milestones.each(function(item) {
            self.addMilestone(item);
        });
    },

    addMilestone: function(item) {
        var mview = new Greenmine.Views.Milestone({model:item});
        this.$("#milestones").append(mview.render().el);
    },

    resetUnassingedUserStories: function() {
        var self = this;
        this.$(".middle-box .list-body").empty();

        Greenmine.Collections.unassignedUserstories.each(function(item) {
            self.addUnassignedUserStory(item);
        });
    },

    addUnassignedUserStory: function(item) {
        var view = new Greenmine.Views.UserStory({model: item});
        this.$(".middle-box .list-body").append(view.render().el);
    }
});

Greenmine.Views.backlog = new Greenmine.Views.Backlog();
