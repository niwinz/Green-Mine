var TaskCreateView = Backbone.View.extend({
    el: $("#task-create"),

    events: {
        'submit form': 'onFormSubmit'
    },

    initialize: function() {
        _.bindAll(this, 'onFormSubmit', 'onSubmitSuccess');
        this.form = new Form({el:this.$("form")});
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

$(function() { new TaskCreateView(); });
