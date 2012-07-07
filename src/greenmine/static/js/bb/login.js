var LoginView = Backbone.View.extend({
    el: $("#login"),

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

$(function() { new LoginView(); });
