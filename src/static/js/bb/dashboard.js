var stats = {
    'open': gettext('New'),
    'progress': gettext('In progress'),
    'completed': gettext('Ready for test'),
    'closed': gettext('Closed'),
};


var UserStory = Backbone.Model.extend({});
var UserStoryCollection = Backbone.Collection.extend({
    model: UserStory
});


var UserStoryView = Backbone.View.extend({
    tagName: 'tr',

    initialize: function() {
        _.bindAll(this, 'render');
        this.model.bind('change', this.render);
        this.model.bind('reset', this.render);
    },

    render: function() {
        this.$el.replaceWith(this.model.get('html'));
        return this;
    }
});


var CreateTaskDialog = Backbone.View.extend({
    events: {
        "submit form": "onFormSubmit",
        "click .form-field input[type=submit].save": "onSaveClicked",
        "click .form-field input[type=submit].save-and-create-other": "onSaveClicked"
    },

    initialize: function() {
        _.bindAll(this, 'show', 'onFormSubmit', 'onFormSubmitSuccess', 'onClose', 'onSaveClicked');
        this.form = this.$("form");
        this.form.find('input[name=createother]').val('off');
        this.form_view = new Form({el: this.form});
    },

    onSaveClicked: function(event) {
        event.preventDefault();

        var target = $(event.currentTarget);
        if (target.hasClass('save-and-create-other')){
            this.$("form input[name=createother]").val('on');
        } else {
            this.$("form input[name=createother]").val('off');
        }
        this.$('form').submit();
    },

    onFormSubmit: function(event) {
        event.preventDefault();
        this.form_view.submit({success: this.onFormSubmitSuccess});
    },

    onFormSubmitSuccess: function(data) {
        if (data.success && data.userStory) {
            var userstory = $("#user-story-" + data.userStory);
            var task = $(data.html);
            this.trigger('new-task', userstory, task, data.status);

            if (this.$("form input[name=createother]").val() == 'on') {
                this.partialClear();
            } else {
                $.colorbox.close();
            }
        } else {
            this.form_view.setErrors(data.errors);
        }
    },

    partialClear: function() {
        this.$('form #id_description').val('');
        this.$('form #id_subject').val('');
    },

    show: function(target) {
        this.$el.removeClass('hidden');

        var userstory = target.closest(".user-story-row");
        var url = userstory.attr('create_task_url');
        var id = userstory.attr('ref');

        this.$('form').attr('action', url);
        this.$('form #id_user_story').val(id);
        this.partialClear();

        target.colorbox({
            inline:true,
            width: '960px',
            onCleanup: this.onClose
        });
    },

    onClose: function(){
        this.$el.addClass('hidden');
    }
});
        


var DashboardView = Backbone.View.extend({
    el: $("#dashboard-matrix"),

    events: {
        "dragstart .task-col .task-container": "onDragStart",
        "dragleave .task-col": "onDragLeave",
        "dragover .task-col": "onDragOver",
        "drop .task-col": "onDrop",

        "change .task-col .task-container .icons .participants": "assignationChangeSelect",
        "change .task-col .task-container .icons .statuses": "statusChangeChange",
        "click .user-story-row .user-story-container .new-task": "onNewTaskClick"
    },

    initialize: function() {
        _.bindAll(this, 'render', 'addOne', 'addAll', 'onDrop',
                        'onDragOver', 'onDragLeave', 'onDragStart',
                        'assignationChangeSelect', 'statusChangeChange',
                        'onNewTaskClick', 'addTask');
        var self = this;

        this.user_stories = new UserStoryCollection();
        this.user_stories_views = new Array();

        _(this.$("tr.user-story-row")).each(function(item) {
            var item = $(item);
            var model_instance = new UserStory({html: item.html(), id: item.attr('ref')})
            var view_instance = new UserStoryView({model:model_instance});
            
            self.user_stories.add(model_instance);
            self.user_stories_views.push(view_instance);
        })

        this.user_stories.bind('add', this.addOne);
        this.create_task_dialog = new CreateTaskDialog({el: $("#create-task-dialog")});
        this.create_task_dialog.on('new-task', this.addTask);
    },
    
    onNewTaskClick: function(event) {
        var target = $(event.currentTarget);
        this.create_task_dialog.show(target);
    },

    addTask: function(userstorydom, taskdom, tstatus) { 
        if (stats[tstatus] === undefined) {
            tstatus = 'closed';
        }

        var coldom = _.find(userstorydom.find('.task-col'), function(item) {
            return $(item).attr('tstatus') == tstatus;
        });

        if (coldom !== undefined) {
            $(coldom).append(taskdom);
        }
    },

    statusChangeChange: function(event) {
        var target = $(event.currentTarget);
        var selected_status_key = target.val()
        var selected_status_text = target.find('option:selected').html();

        var userstory = target.closest('.user-story-row');
        var task = target.closest('.task-container');

        task.removeClass('non-closed-task');
        var self = this;
        
        var post_callback = function() {
            self.addTask(userstory, task, selected_status_key);
            task.attr('current_status', selected_status_key);
        };

        var url = task.attr('alter_url');
        var data = {'status': selected_status_key};

        $.post(url, data, function(data) {
            if (data.valid) { post_callback(); }
        }, 'json');
    },

    assignationChangeSelect: function(event) {
        var self = $(event.currentTarget);
        var selected_person_id = self.val();
        var selected_person_name = self.find('option:selected').html();
        var url = self.closest(".task-container").attr('reasign_url');

        $.post(url, {userid:selected_person_id}, function(data) {
            if (data.valid) {
            }
        }, 'json');
    },

    onDragStart: function(event) {
        var self = $(event.currentTarget);
        event.originalEvent.dataTransfer.effectAllowed = 'copy';
        event.originalEvent.dataTransfer.setData('source_id', self.attr('id'));
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
        var self = $(event.currentTarget);
        
        if (self.hasClass('drag-over')) {
            self.removeClass('drag-over');
        }

        var source_id = event.originalEvent.dataTransfer.getData('source_id');
        var source = $("#" + source_id);
        var current_source_status = source.attr('current_status');
        var source_parent = source.closest('td');

        var userstory = self.closest('tr');
        var userstory_id = userstory.attr('ref');

        var status_node = source.find('.current-status');
        var new_status_string = null;

        if (stats[current_source_status] === undefined) {
            new_status_string = current_source_status;
        } else {
            new_status_string = self.attr('tstatus');

            // Remove some classes added on status change
            source.removeClass('non-closed-task');
            source.attr('current_status', new_status_string);

            // Set new status and new status representation text
            status_node.attr('status', new_status_string);
            status_node.html(stats[new_status_string]);
        }

        // Move dom
        self.append(source);

        var url = source.attr('alter_url');
        var data = {
            'status': new_status_string
        };

        if (userstory_id) {
            data['us'] = userstory_id;
        }

        $.post(url, data, function(data) {
            if (!data.valid) {
                source_parent.append(source);
            }
        }, 'json');
    },

    addOne: function(item) {
        var view = new UserStoryView({model:item});
        this.$("table tbody").append(view.render().el);
    },

    addAll: function() {
        this.user_stories.each(this.addOne);
    },

    render: function() {},
});

var dashboard = new DashboardView();
