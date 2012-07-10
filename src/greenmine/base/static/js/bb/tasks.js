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
        "click .context-menu a.filter-task": "changeStatus",

        /*Tag filtering */
        //"click .un-us-item .category.selected": "on_tag_remove_filter_clicked",
        //"click .un-us-item .category.unselected": "on_tag_add_filter_clicked"
        "click .un-us-item .category": "on_tag_add_filter_clicked"
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

        var order_by = getUrlVars()["order_by"];
        if (order_by === undefined){
            this.options.order_by = "-priority";
        }
        else{
            this.options.order_by = order_by;
        }

        this.options.tag_filter = getIntListFromURLParam('tags');

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
            "tags": this.options.tag_filter
        }
        if (this._status.length > 0) {
            current['status'] = this._status;
        }
        return current;
    },

    reload: function(post_data) {
        var url = this.$el.data('tasks-url');
        var post_data = this.collectPostData();

        $.post(url, post_data, function(data) {
            console.log(data);

            Greenmine.tagCollection.reset(data.tags);
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
    },

    on_tag_add_filter_clicked: function(){
        event.preventDefault();
        var self = $(event.target);
        var tag_filter = parseInt(self.attr('category'));

        if ($.inArray(tag_filter, this.options.tag_filter)<0){
            this.options.tag_filter.push(tag_filter);
            this.reload();
        }
    }
});
