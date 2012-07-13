var stats = {
    'open': gettext('New'),
    'progress': gettext('In progress'),
    'completed': gettext('Ready for test'),
    'closed': gettext('Closed'),
};

var Greenmine = {}

Greenmine.UserStory = Backbone.Model.extend({});
Greenmine.UserStoryCollection = Backbone.Collection.extend({
    model: Greenmine.UserStory
});

Greenmine.Task = Backbone.Model.extend({});
Greenmine.TaskCollection = Backbone.Collection.extend({
    model: Greenmine.Task
});


Greenmine.UserStoryView = Backbone.View.extend({
    tagName: "div",

    attributes: {
        'class': 'userstory-item'
    },

    initialize: function() {
        _.bindAll(this);
    },

    render: function() {
        this.$el.html(Greenmine.usTemplate(this.model.toJSON()));
        this.$el.attr('id', 'user-story-' + this.model.get('id'));
        this.$el.attr('data-id', this.model.get('id'));
        return this;
    }
});


Greenmine.TaskView = Backbone.View.extend({
    tagName: "div",

    attributes: {
        "class": "task-item",
        "draggable": "true",
    },

    render: function() {
        var context = this.model.toJSON();
        context = _.extend(context, {
            'participants': Greenmine.participants,
            'statuses': Greenmine.statuses
        });

        this.$el.html(Greenmine.taskTemplate(context));
        this.$el.attr('id', 'task-' +  this.model.get('id'));
        this.$el.attr('data-id',  this.model.get('id'));
        this.$el.attr('data-status', this.model.get('status'));
        return this;
    },

    setStatus: function(stat) {
        this.$el.attr('data-status', stat);
        this.model.set('status', stat);
        this.$(".status-button").html(stats[stat]);
    },

    setUserStory: function(us) {
        this.model.set('us', us);
    },

    setAssigation: function(person) {
        this.model.set("assignedTo", person);
    }
});

Greenmine.usCollection = new Greenmine.UserStoryCollection();
Greenmine.taskCollection = new Greenmine.TaskCollection();

Greenmine.usTemplate = doT.template($("#userstory-template").html());
Greenmine.taskTemplate = doT.template($("#userstory-task-template").html());

/* Create dialog */

Greenmine.CreateTaskDialog = Kaleidos.Lightbox.extend({
    el: "#new-task-lightbox",

    events: {
        'click a.close-lightbox': 'onCloseClicked',
        'click a.accept-lightbox': 'onAcceptClicked',
        "click .newtask-meta .button.plus": "newTaskDom"
    },

    _initilize: function() {

    },

    collectTasks: function() {
        var tasks = new Array();
        _.each(this.$("textarea"), function(item) {
            tasks.push($(item).val());
        });

        return tasks;
    },

    _close: function(ok) {
        console.log(this.$el, this.$el.data());
        var self = this;
        if (ok) {
            var context = {
                task: this.collectTasks(),
                us: this.userStoryReference
            };

            $.post(this.$el.data('url'),  context, function(data) {
                self.trigger("newTasks", data.tasks);
            }, 'json');
        }
    },

    newTaskDom: function() {
        var new_formset = this.$(".formset-item").eq(0).clone();
        new_formset.find("textarea").val("");

        this.$(".newtask-formset").append(new_formset);
    },

    setUserStoryReference: function(ref) {
        this.userStoryReference = ref;
    }
});

Greenmine.createDialog = new Greenmine.CreateTaskDialog();

/* Dashboard view */

Greenmine.DashboardView = Backbone.View.extend({
    el: $("#milestone-dashboard"),

    events: {
        "dragstart td.status .task-item": "onDragStart",
        "dragleave td.status": "onDragLeave",
        "dragover td.status": "onDragOver",
        "drop td.status": "onDrop",
        "click .button-newtask": "newTaskDialog",
    },

    initialize: function() {
        _.bindAll(this);

        Greenmine.usCollection.on("reset", this.resetUserStories);
        Greenmine.taskCollection.on("reset", this.resetTasks);
        Greenmine.taskCollection.on("add", this.addTask);

        Greenmine.createDialog.on("newTasks", this.onNewTasks);


        this.tasks = [];
        this.uss = [];
    },

    onNewTasks: function(tasks) {
        console.log(tasks);
        Greenmine.taskCollection.add(tasks);
    },

    newTaskDialog: function(event) {
        event.preventDefault();

        var target = $(event.currentTarget);
        var userStory = target.closest(".userstory-item");

        Greenmine.createDialog.setUserStoryReference(userStory.data('id'));
        Greenmine.createDialog.open();
    },

    resetUserStories: function() {
        var self = this;
        self.uss = [];
        Greenmine.usCollection.each(function(item) {
            self.addUserStory(item);
        });
    },

    addUserStory: function(item) {
        var view = new Greenmine.UserStoryView({model:item});
        this.$(".userstory-list").append(view.render().el);
    },

    resetTasks: function() {
        var self = this;
        self.tasks = [];
        Greenmine.taskCollection.each(function(item) {
            self.addTask(item);
        });
    },

    addTask: function(item) {
        var view = new Greenmine.TaskView({model:item});

        var usdom = this.$("#user-story-" + item.get("us"));
        var column = _.find(usdom.find("td.status"), function(element) {
            return $(element).data('status') == item.get('fakeStatus');
        });

        $(column).find(".task-item-container").append(view.render().el);
        this.tasks.push(view);
    },

    onDragStart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy';
        event.originalEvent.dataTransfer.setData('id', self.data('id'));
    },

    onDragLeave: function(event) {
        var self = $(event.currentTarget);
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }
    },

    onDragOver: function(event) {
        event.originalEvent.dataTransfer.dropEffect = 'copy';
        event.preventDefault();
        var self = $(event.currentTarget);

        if (!self.hasClass("drag-over")) {
            self.addClass("drag-over");
        }
    },

    onDrop: function(event) {
        var column = $(event.currentTarget);

        if (column.hasClass('drag-over')) {
            column.removeClass('drag-over');
        }

        var id = event.originalEvent.dataTransfer.getData('id');
        var task_view = _.find(this.tasks, function(taskview) {
            return taskview.model.get('id') == id;
        });

        var userstory = column.closest('.userstory-item');

        var new_status_string = null;
        if (stats[task_view.model.get('status')] === undefined) {
            new_status_string = task_view.model.get('status');
        } else {
            new_status_string = column.data('status');
        }

        task_view.setStatus(new_status_string);
        task_view.setUserStory(userstory.data('id'));
        column.find(".task-item-container").append(task_view.$el);

        var apiUrl = this.$el.data('api-url');

        var postData = {
            "status": new_status_string,
            "us": userstory.data('id'),
            "task":  id,
            "assignation": task_view.model.get('assignedTo') || ""
        }

        $.post(apiUrl, postData, function(response) {
        }, 'json');
    }
});

Greenmine.SprintBurndownModel = Backbone.Model.extend({
    url: function() {
        return this.get('view').$el.data('url');
    }
});

Greenmine.SprintBurndownView = Backbone.View.extend({
    el: $("#sprint-burndown"),

    initialize: function() {
        _.bindAll(this, 'render', 'reload');
        if (this.$el.attr('show') === 'on') {
            this.model = new Greenmine.SprintBurndownModel({'view':this});
            this.model.fetch({success:this.render});
        }
    },

    reload: function() {
        if (this.$el.attr('show') === 'on') {
            this.model.fetch({success:this.render});
        }
    },

    render: function() {
        if (this.$el.attr('show') !== 'on') {
            return;
        }

        this.$("#sprint-burndown-graph").show();

        var d1 = new Array(),
            d2 = new Array(),
            ticks = new Array();

        var begin_date = new Date(this.model.get('begin_date'));
        var end_date = new Date(this.model.get('end_date'));
        var sprint_points = this.model.get('sprint_points');
        var points_done_on_date = this.model.get('points_done_on_date');
        var now_position = this.model.get('now_position');

        var counter = 1;
        ticks.push([1, "Kickoff"]);
        for(var date=new Date(begin_date.toString()); date<=end_date; date.setDate(date.getDate()+1)) {
            ticks.push([counter+1, date.getDate().toString()+"/"+(date.getMonth()+1).toString()]);
            counter++;
        }

        for(var i=0; i<=ticks.length-1; i++) {
            if(now_position<i+1) {
                d1.push([now_position, sprint_points-points_done_on_date[i]]);
            } else {
                d1.push([i+1, sprint_points-points_done_on_date[i]]);
            }
            d2.push([i+1, sprint_points-((sprint_points/ticks.length)*i)]);
        }

        $.plot(this.$('#sprint-burndown-graph'), [
            {
                data: d1,
                lines: { show: true, fill: false },
                points: { show: true },
                color: "#669900"
            },
            {
                data: d2,
                lines: { show: true, fill: true },
                points: { show: true },
                color: '#eec446'
            },
            {
                data: [[now_position, 0], [now_position, sprint_points+5]],
                lines: { show: true, fill: true },
                points: { show: false },
                color: "#888888",
            }
        ],
        {
            xaxis: { ticks: ticks },
            yaxis: { position: "right", labelWidth: 20 },
            grid: { borderWidth: 0 }
        });
    }
});
