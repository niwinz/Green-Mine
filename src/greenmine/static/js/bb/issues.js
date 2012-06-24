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

Greenmine.TaskModel = Backbone.Model.extend({});

Greenmine.TaskCollection = Backbone.Collection.extend({
    model: Greenmine.TaskModel
});

Greenmine.taskCollection = new Greenmine.TaskCollection();
Greenmine.template = doT.template($("#task-template").html());

Greenmine.TaskView = Backbone.View.extend({
    tagName: "div",
    attributes: {
        "class": "un-us-item"
    },

    initialize: function() {
        _.bindAll(this);
    },

    render: function() {
        this.$el.html(Greenmine.template(this.model.toJSON()));
        this.$el.attr({
            'data-id':this.model.get('id'),
            'id': "issue_" + this.model.get('id')
        });
        return this;
    }
});

Greenmine.IssuesView = Backbone.View.extend({
    events: {
        "click .un-us-item img.delete": "deleteIssueClick"
    },

    el: $("#dashboard"),
    
    initialize: function() {
        _.bindAll(this);
        Greenmine.taskCollection.on("reset", this.reset);
        Greenmine.taskCollection.on("remove", this.deleteIssue);

        this.lightbox = new Greenmine.Lightbox({
            el: $("#delete-issue-dialog")
        });
    },

    deleteIssueClick: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget).closest('.un-us-item');
        var issue = Greenmine.taskCollection.get(target.data('id'));

        this.lightbox.setReference(issue);
        this.lightbox.open();
        this.lightbox.on('delete', this.deleteIssue);
    },

    addIssue: function(issue) {
        var view = new Greenmine.TaskView({model:issue});
        this.$("#issue-list-body").append(view.render().el);
    },

    deleteIssue: function(issue) {
        var self = this;
        $.post(issue.get('delete_url'), {}, function(data) {
            if (data.valid) {
                var selector = "#issue_" + issue.get('id');
                self.$(selector).remove();
            }
        }, 'json');
    },
    
    reset: function() {
        var self = this;
        Greenmine.taskCollection.each(function(item) {
            self.addIssue(item);
        });
    }
});
