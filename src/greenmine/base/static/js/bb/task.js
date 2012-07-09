if (window.Greenmine === undefined) {
    window.Greenmine = {};
}

Greenmine.TaskCreateView = Backbone.View.extend({
    // DEPRECATED
    el: $("#task-create"),

    events: {
        'submit form': 'onFormSubmit'
    },

    initialize: function() {
        _.bindAll(this, 'onFormSubmit', 'onSubmitSuccess');
        this.form = new Kaleidos.Form({el:this.$("form")});
    },

    onFormSubmit: function(event) {
        event.preventDefault();

        this.form.submit({
            success: this.onSubmitSuccess
        });
    },

    onSubmitSuccess:function(data) {
        if (data.success) {
            if (data.redirect_to) {
                window.location.href = data.redirect_to;
            }
        } else {
            this.form.setErrors(data.errors)
        }
    }
});

/* Issue detail view */
Greenmine.IssueView = Backbone.View.extend({
    el: $("#issues-view"),

    events: {
        "submit .response-form form": "onFormSubmit"
    },

    initialize: function() {
        _.bindAll(this);
        this.form = new Kaleidos.Form({el:this.$(".response-form form")});
    },

    onFormSubmit: function(event) {
        event.preventDefault();

        this.form.submit({success:this.onSubmitSuccess});
    },

    onSubmitSuccess: function(data) {
        if (!data.valid) {
            return;
        }

        this.$(".task-changes .changes-list").append(data.html);
        this.form.reset();
    }
});

Greenmine.TaskView = Greenmine.IssueView.extend({
    el: $("#tasks-view")
});

if ($("#task-create").length) {
    new Greenmine.TaskCreateView();
}
