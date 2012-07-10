var Greenmine = {}

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

/*Tags*/
Greenmine.TagModel = Backbone.Model.extend({});

Greenmine.TagCollection = Backbone.Collection.extend({
    model: Greenmine.TagModel
});

Greenmine.tagCollection = new Greenmine.TagCollection();
Greenmine.tag_template = doT.template($("#tag-template").html());

Greenmine.TagView = Backbone.View.extend({
    tagName: "span",

    render: function() {

        this.$el.html(Greenmine.tag_template(this.model.toJSON()));
        return this;
    }
});

/*Tasks*/
Greenmine.TaskModel = Backbone.Model.extend({});

Greenmine.TaskCollection = Backbone.Collection.extend({
    model: Greenmine.TaskModel
});

Greenmine.taskCollection = new Greenmine.TaskCollection();
Greenmine.task_template = doT.template($("#task-template").html());

Greenmine.TaskView = Backbone.View.extend({
    tagName: "div",
    attributes: {
        "class": "un-us-item"
    },

    render: function() {
        this.$el.html(Greenmine.task_template(this.model.toJSON()));
        this.$el.attr({
            'data-id':this.model.get('id'),
            'id': "task_" + this.model.get('id')
        });
        return this;
    }
});

Greenmine.TasksView = Backbone.View.extend({
    events: {
        "click .un-us-item img.delete": "deleteIssueClick",
        "click .un-us-item.head-title .row a": "changeOrder",
        "click .context-menu a.filter-task": "changeStatus"
    },

    el: $("#dashboard"),

    initialize: function() {
        _.bindAll(this);
        Greenmine.taskCollection.on("reset", this.reset);
        Greenmine.taskCollection.on("remove", this.deleteIssue);

        this.lightbox = new Greenmine.Lightbox({
            el: $("#delete-task-dialog")
        });

        this._milestone_id = this.$el.data('milestone');
        this._order = "created_date";
        this._order_mod = "-";
        this._status = "closed";
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

    changeMilestone: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget).closest('.milestone-item');
        this._milestone_id = target.data('id');
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
            "milestone": this._milestone_id,
        }
        if (this._status.length > 0) {
            current['status'] = this._status;
        }
        return current;
    },

    reload: function(post_data) {
        var url = this.$el.data('tasks-url');

        if (post_data === undefined) {
            post_data = {};
        }

        var postdata = _.extend({}, this.collectPostData(), post_data);

        $.post(url, postdata, function(data) {
            Greenmine.taskCollection.reset(data.tasks);
        }, 'json');
    },

    deleteIssueClick: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget).closest('.un-us-item');
        var task = Greenmine.taskCollection.get(target.data('id'));

        this.lightbox.setReference(task);
        this.lightbox.open();
        this.lightbox.on('delete', this.deleteIssue);
    },

    addIssue: function(task) {
        var view = new Greenmine.TaskView({model:task});
        this.$("#task-list-body").append(view.render().el);
    },

    addTag: function(tag) {
        var view = new Greenmine.TagView({model:tag});
        this.$("#tags-body").append(view.render().el);
    },

    deleteIssue: function(task) {
        var self = this;
        $.post(task.get('delete_url'), {}, function(data) {
            if (data.valid) {
                var selector = "#task_" + task.get('id');
                self.$(selector).remove();
            }
        }, 'json');
    },

    reset: function() {
        var self = this;
        this.$("#task-list-body").html("");
        Greenmine.taskCollection.each(function(item) {
            self.addIssue(item);
        });
        this.$("#tags-body").html("");
        Greenmine.tagCollection.each(function(item) {
            self.addTag(item);
        });
    }
});
