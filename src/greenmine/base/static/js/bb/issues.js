/* Initial */

Greenmine.Filters = {};

/* Models */

Greenmine.MilestoneModel = Backbone.Model.extend({});
Greenmine.TaskModel = Backbone.Model.extend({});

Greenmine.Filters.TagModel = Backbone.Model.extend({});
Greenmine.Filters.StatusModel = Backbone.Model.extend({});
Greenmine.Filters.AssignedToModel = Backbone.Model.extend({});
Greenmine.Filters.SeverityModel = Backbone.Model.extend({});



/* Collections */

Greenmine.MilestoneCollection = Backbone.Collection.extend({
    model: Greenmine.MilestoneModel
});

Greenmine.TaskCollection = Backbone.Collection.extend({
    model: Greenmine.TaskModel
});

Greenmine.Filters.TagCollection = Backbone.Collection.extend({
    model: Greenmine.Filters.TagModel
});

Greenmine.Filters.StatusCollection = Backbone.Collection.extend({
    model: Greenmine.Filters.StatusModel
});

Greenmine.Filters.AssignedToCollection = Backbone.Collection.extend({
    model: Greenmine.Filters.AssignedToModel
});

Greenmine.Filters.SeverityCollection = Backbone.Collection.extend({
    model: Greenmine.Filters.SeverityModel
});


Greenmine.milestoneCollection = new Greenmine.MilestoneCollection();
Greenmine.taskCollection = new Greenmine.TaskCollection();

Greenmine.Filters.tagCollection = new Greenmine.Filters.TagCollection();
Greenmine.Filters.statusCollection = new Greenmine.Filters.StatusCollection();
Greenmine.Filters.assignedToCollection = new Greenmine.Filters.AssignedToCollection();
Greenmine.Filters.severityCollection = new Greenmine.Filters.SeverityCollection();


/* Templates */

Greenmine.filter_template = doT.template($("#filter-template").html());
Greenmine.task_template = doT.template($("#task-template").html());


/* Views */

Greenmine.Lightbox = Kaleidos.Lightbox.extend({
    events: {
        'click a.close': 'onCloseClicked',
        'click a.delete': 'onDeleteClicked'
    },

    setReference: function(ref) {
        this.ref = ref;
    },

    onDeleteClicked: function(event) {
        event.preventDefault();
        this.close();
        this.trigger("delete", this.ref);
    }
});

Greenmine.MilestoneView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "milestone"
    },
    render: function() {
        this.$el.html(Greenmine.filter_template(this.model.toJSON()));
        return this;
    }
});

Greenmine.Filters.TagView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "tag"
    },
    render: function() {
        this.$el.html(Greenmine.filter_template(this.model.toJSON()));
        return this;
    }
});

Greenmine.Filters.StatusView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "status"
    },
    render: function() {
        this.$el.html(Greenmine.filter_template(this.model.toJSON()));
        return this;
    }
});

Greenmine.Filters.AssignedToView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "assigned-to"
    },
    render: function() {
        this.$el.html(Greenmine.filter_template(this.model.toJSON()));
        return this;
    }
});

Greenmine.Filters.SeverityView = Backbone.View.extend({
    tagName: "span",
    attributes: {
        "class": "severity"
    },
    render: function() {
        this.$el.html(Greenmine.filter_template(this.model.toJSON()));
        return this;
    }
});

Greenmine.TaskView = Backbone.View.extend({
    tagName: "div",
    attributes: {
        "class": "list-item"
    },

    render: function() {
        var context = this.model.toJSON();
        context = _.extend(context, {
            'participants': Greenmine.participants,
            'statuses': Greenmine.statuses,
        });

        this.$el.html(Greenmine.task_template(context));
        this.$el.attr({
            'data-id':this.model.get('id'),
            'id': "task_" + this.model.get('id')
        });
        return this;
    },

    // DEPRECATED
    getParticipantById: function(id) {
        var val = _.find(Greenmine.participants,  function(item) {
            return item['id'] == id;
        });

        if (val) {
            return val[name];
        } else {
            return null;
        }
    }
});

Greenmine.TasksView = Backbone.View.extend({
    events: {
        //TODO: fix this three selectors
        "click .un-us-item.head-title .row a": "changeOrder",
        "click .context-menu a.filter-task": "changeStatus",

        /*Tag filtering */
        "click .category.selected": "on_tag_remove_filter_clicked",
        "click .category.unselected": "on_tag_add_filter_clicked",

        /*Milestone filtering */
        "click .milestone .category.selected": "on_milestone_remove_filter_clicked",
        "click .milestone .category.unselected": "on_milestone_add_filter_clicked",

        /*Status filtering */
        "click .status .category.selected": "on_status_remove_filter_clicked",
        "click .status .category.unselected": "on_status_add_filter_clicked",

        /*Assigned to filtering */
        "click .assigned-to .category.selected": "on_assigned_remove_filter_clicked",
        "click .assigned-to .category.unselected": "on_assigned_add_filter_clicked",

        /*Severity*/
        "click .severity .category.selected": "on_severity_remove_filter_clicked",
        "click .severity .category.unselected": "on_severity_add_filter_clicked",

        /*Filters box*/
        "click .filters-bar .show-hide-filters-box": "toggle_filters_box_visibility",
        "click .filters-bar .remove-filters": "remove_filters",
        "click .filters-container .filter-section": "toggle_filter_section",

        "click .list-body .list-item a.delete": "deleteIssueClick",
    },

    el: $("#issues"),

    initialize: function() {
        _.bindAll(this);

        Greenmine.taskCollection.on("reset", this.reset);
        Greenmine.taskCollection.on("remove", this.deleteIssue);

        this.lightbox = new Greenmine.Lightbox({el: $("#issues-delete-dialog")});
        this.lightbox.on('delete', this.deleteIssue);

        this._milestone_id = this.$el.data('milestone');
        this._order = "created_date";
        this._order_mod = "-";
        this._status = "";

        var order_by = getUrlVars()["order_by"];
        if (order_by === undefined){
            this.options.order_by = "-priority";
        } else {
            this.options.order_by = order_by;
        }

        this.options.tag_filter = getIntListFromURLParam('tags');
        this.options.milestone_filter = getIntListFromURLParam('milestone');

        var base_status_filter = getUrlVars()['status'];

        this.options.status_filter = getStringListFromURLParam('status');
        this.options.assigned_to_filter = getIntListFromURLParam('assigned_to');
        this.options.severity_filter = getIntListFromURLParam('severity');
        this.filters_box_visible = false;
    },

    changeOrder: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget);

        if (this._order == target.data('type')) {
            if (this._order_mod == '-') {
                this._order_mod = '';
            } else {
                this._order_mod = '-';
            }
        } else {
            this._order = target.data('type');
            this._order_mod = '-';
        }

        this.reload();
    },

    changeStatus: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        this._status = target.data('type');
        this.reload();
    },

    collectPostData: function() {
        var current = {
            "order_by": this._order_mod + this._order,
            "milestone": this.options.milestone_filter,
            "tags": this.options.tag_filter,
            "status": this.options.status_filter,
            "assigned_to": this.options.assigned_to_filter,
            "severity": this.options.severity_filter
        }
        return current;
    },

    reload: function(post_data) {
        var url = this.$el.data('tasks-url');

        var post_data = this.collectPostData();

        if (typeof(window.history.pushState) == 'function'){
            history.pushState({}, "issues ", "?"+$.param(post_data));
        }

        $.get(url, post_data, function(data) {
            Greenmine.Filters.tagCollection.reset(data.filter_dict.tags);
            Greenmine.Filters.statusCollection.reset(data.filter_dict.status);
            Greenmine.Filters.assignedToCollection.reset(data.filter_dict.assigned_to);
            Greenmine.Filters.severityCollection.reset(data.filter_dict.severity);
            Greenmine.milestoneCollection.reset(data.filter_dict.milestones);
            Greenmine.taskCollection.reset(data.tasks);
        }, 'json');
    },

    deleteIssueClick: function(event) {
        event.preventDefault();

        var target = $(event.currentTarget).closest('.list-item');
        var task = Greenmine.taskCollection.get(target.data('id'));

        this.lightbox.setReference(task);
        this.lightbox.open();
    },

    addIssue: function(task) {
        var view = new Greenmine.TaskView({model:task});
        this.$(".list-body").append(view.render().el);
    },

    addTag: function(tag) {
        var view = new Greenmine.Filters.TagView({model:tag});
        var rendered_elem = view.render().el;
        this.$("#tags-body").append(rendered_elem);
        if (tag.attributes.selected === true){
            this.$("#selected-filters").append($(rendered_elem).clone());
        }
    },

    addMilestone: function(tag) {
        var view = new Greenmine.MilestoneView({model:tag});
        var rendered_elem = view.render().el;
        this.$("#milestones-body").append(rendered_elem);
        if (tag.attributes.selected === true){
            this.$("#selected-filters").append($(rendered_elem).clone());
        }
    },

    addStatus: function(tag) {
        var view = new Greenmine.Filters.StatusView({model:tag});
        var rendered_elem = view.render().el;
        this.$("#status-body").append(rendered_elem);
        if (tag.attributes.selected === true){
            this.$("#selected-filters").append($(rendered_elem).clone());
        }
    },

    addAssignedTo: function(tag) {
        var view = new Greenmine.Filters.AssignedToView({model:tag});
        var rendered_elem = view.render().el;
        this.$("#assigned-to-body").append(rendered_elem);
        if (tag.attributes.selected === true){
            this.$("#selected-filters").append($(rendered_elem).clone());
        }
    },

    addSeverity: function(tag) {
        var view = new Greenmine.Filters.SeverityView({model:tag});
        var rendered_elem = view.render().el;
        this.$("#severity-body").append(rendered_elem);
        if (tag.attributes.selected === true){
            this.$("#selected-filters").append($(rendered_elem).clone());
        }
    },

    deleteIssue: function(task) {
        var self = this;

        $.post(task.get('deleteUrl'), {}, function(data) {
            if (data.success) {
                var object = self.$("#task_" + task.get('id'));
                object.slideUp("fast", function() {
                    object.remove();
                });
            }
        }, 'json');
    },

    reset: function() {
        var self = this;

        this.$("#selected-filters").html("");

        this.$(".list-body").html("");

        Greenmine.taskCollection.each(function(item) {
            self.addIssue(item);
        });

        this.$("#milestones-body").html("");
        Greenmine.milestoneCollection.each(function(item) {
            self.addMilestone(item);
        });
        this.$("#milestones-filter-section").toggle(Greenmine.milestoneCollection.length!=0);

        this.$("#tags-body").html("");
        Greenmine.Filters.tagCollection.each(function(item) {
            self.addTag(item);
        });
        this.$("#tags-filter-section").toggle(Greenmine.Filters.tagCollection.length!=0);

        this.$("#status-body").html("");
        Greenmine.Filters.statusCollection.each(function(item) {
            self.addStatus(item);
        });
        this.$("#status-filter-section").toggle(Greenmine.Filters.statusCollection.length!=0);

        this.$("#assigned-to-body").html("");
        Greenmine.Filters.assignedToCollection.each(function(item) {
            self.addAssignedTo(item);
        });
        this.$("#assigned-to-filter-section").toggle(Greenmine.Filters.assignedToCollection.length!=0);

        this.$("#severity-body").html("");
        Greenmine.Filters.severityCollection.each(function(item) {
            self.addSeverity(item);
        });
        this.$("#severity-filter").toggle(Greenmine.Filters.severityCollection.length!=0);

        if (this.$("#selected-filters .category").length > 0) {
            this.$(".remove-filters").show();
        }
        else {
            this.$(".remove-filters").hide();
        }

        Greenmine.main.colorizeTags();
    },

    on_tag_add_filter_clicked: function(event){
        event.preventDefault();
        var self = $(event.target);
        var tag_filter = parseInt(self.attr('category'));

        if ($.inArray(tag_filter, this.options.tag_filter)<0){
            this.options.tag_filter.push(tag_filter);
            this.reload();
        }
    },

    on_tag_remove_filter_clicked: function(event){
        event.preventDefault();
        event.stopPropagation();
        var self = $(event.target);
        var tag_filter = parseInt(self.attr('category'));
        this.options.tag_filter.pop(tag_filter);
        this.reload();
    },

    on_milestone_add_filter_clicked: function(event){
        event.preventDefault();
        var self = $(event.target);
        var milestone_filter = parseInt(self.attr('category'));
        if ($.inArray(milestone_filter, this.options.milestone_filter)<0){
            this.options.milestone_filter.push(milestone_filter);
            this.reload();
        }
    },

    on_milestone_remove_filter_clicked: function(event){
        event.preventDefault();
        event.stopPropagation();
        var self = $(event.target);
        var milestone_filter = parseInt(self.attr('category'));
        this.options.milestone_filter.pop(milestone_filter);
        this.reload();
    },

    on_status_add_filter_clicked: function(event){
        event.preventDefault();
        var self = $(event.target);
        var status_filter = self.attr('category');
        if ($.inArray(status_filter, this.options.status_filter)<0){
            this.options.status_filter.push(status_filter);
            this.reload();
        }
    },

    on_status_remove_filter_clicked: function(event){
        event.preventDefault();
        event.stopPropagation();
        var self = $(event.target);
        var status_filter = parseInt(self.attr('category'));
        this.options.status_filter.pop(status_filter);
        this.reload();
    },

    on_assigned_add_filter_clicked: function(event){
        event.preventDefault();
        var self = $(event.target);
        var assigned_to_filter = parseInt(self.attr('category'));
        if ($.inArray(assigned_to_filter, this.options.assigned_to_filter)<0){
            this.options.assigned_to_filter.push(assigned_to_filter);
            this.reload();
        }
    },

    on_assigned_remove_filter_clicked: function(event){
        event.preventDefault();
        event.stopPropagation();
        var self = $(event.target);
        var assigned_to_filter = parseInt(self.attr('category'));
        this.options.assigned_to_filter.pop(assigned_to_filter);
        this.reload();
    },

    on_severity_add_filter_clicked: function(event){
        event.preventDefault();
        var self = $(event.target);
        var severity_filter = parseInt(self.attr('category'));
        if ($.inArray(severity_filter, this.options.severity_filter)<0){
            this.options.severity_filter.push(severity_filter);
            this.reload();
        }
    },

    on_severity_remove_filter_clicked: function(event){
        event.preventDefault();
        event.stopPropagation();
        var self = $(event.target);
        var severity_filter = parseInt(self.attr('category'));
        this.options.severity_filter.pop(severity_filter);
        this.reload();
    },

    toggle_filter_section: function(event) {
        var related = $(event.target).attr('related');
        this.$(".filter-group").removeClass('selected');
        $(related).addClass('selected');
    },

    toggle_filters_box_visibility: function(event) {
        this.$('.filters-container').toggle();
        this.filters_box_visible = this.$('.filters-container').is(":visible");
    },

    remove_filters: function(event){
        this.options.tag_filter = [];

        this.options.milestone_filter = [];
        var base_status_filter = undefined;
        this.options.status_filter = [];
        this.options.assigned_to_filter = [];
        this.options.severity_filter = [];

        this.reload();
    }

});
