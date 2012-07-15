Greenmine.GenericFormsView = Backbone.View.extend({
    events: {
        "click .area-item.data-url": "submit"
    },

    initialize: function() {
        _.bindAll(this);
        this.form = new Kaleidos.Form({el: this.$("form")});
        this.form.on("success", this.postSuccess);
    },

    submit: function(event) {
        event.preventDefault();

        var target = $(event.currentTarget);
        if (target.data('value') == '1') {
            this.form.submit();
        }
    },

    postSuccess: function(data) {
        if (!data.success) {
            this.form.setErrors(data.errors);
        } else {

            if (data.redirect_to) {
                window.location.href = data.redirect_to;
            }
        }
    }
});

_.each($(".form-box").not('.no-backbone-view'), function(item) {
    new Greenmine.GenericFormsView({el: $(item)});
});
