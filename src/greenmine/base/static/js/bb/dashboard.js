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


Greenmine.DashboardView = Backbone.View.extend({
    el: $("#milestone-dashboard"),

    events: {
        "dragstart td.status .task-item": "onDragStart",
        "dragleave td.status": "onDragLeave",
        "dragover td.status": "onDragOver",
        "drop td.status": "onDrop",

        //"change .task-col .task-container .icons .participants": "assignationChangeSelect",
        //"change .task-col .task-container .icons .statuses": "statusChangeChange"
        //"click .user-story-row .user-story-container .new-task": "onNewTaskClick"
    },

    initialize: function() {
        _.bindAll(this);

        Greenmine.usCollection.on("reset", this.resetUserStories);
        Greenmine.taskCollection.on("reset", this.resetTasks);

        this.tasks = [];
        this.uss = [];
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
    },

    assignationChangeSelect: function(event) {
        var target = $(event.currentTarget);
        var selected_person_id = target.val();

        var task_dom = target.closest(".task-container");
        var us_dom = task_dom.closest("tr.user-story-row");

        var task_view = _.find(this.tasks, function(taskview) {
            return taskview.model.get('id') == task_dom.data('id');
        });

        task_view.setAssigation(selected_person_id);

        var postData = {
            "assignation": selected_person_id,
            "task": task_dom.data('id'),
            "status": task_dom.data('status'),
            "us": us_dom.data('id')
        };

        var apiUrl = this.$el.data('api-url');

        $.post(apiUrl, postData, function(response) {
            console.log(response);
        }, 'json');
    },

    statusChangeChange: function(event) {
        var target = $(event.currentTarget);
        var selected_status_key = target.val()

        var task_dom = target.closest(".task-container");
        var us_dom = task_dom.closest("tr.user-story-row");

        var task_view = _.find(this.tasks, function(taskview) {
            return taskview.model.get('id') == task_dom.data('id');
        });

        var postData = {
            "assignation": task_view.model.get('assignedTo'),
            "task": task_dom.data('id'),
            "status": selected_status_key,
            "us": us_dom.data('id')
        };

        task_view.setStatus(selected_status_key);

        var apiUrl = this.$el.data('api-url');

        $.post(apiUrl, postData, function(response) {
            if (!response.success) return;
            var column = _.find(us_dom.find(".task-col"), function(element) {
                return $(element).data('status') == response.task.fakeStatus;
            });
            $(column).append(task_view.$el);
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
        for(var date=new Date(begin_date.toString()); date<=end_date; date.setDate(date.getDate()+1)) {
            ticks.push([counter, date.getDate().toString()+"/"+(date.getMonth()+1).toString()]);
            counter++;
        }

        for(var i=0; i<=ticks.length; i++) {
            d1.push([i+1, sprint_points-points_done_on_date[i]]);
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
                data: [[now_position, 0], [now_position, sprint_points]],
                lines: { show: true, fill: true },
                points: { show: false },
                color: "#ff9900"
            }
        ],
        {
            xaxis: { ticks: ticks },
            grid: { borderWidth: 0 }
        });
    }
});
