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
        console.log(1);

        var target = $(event.currentTarget);
        if (target.data('value') == '1') {
            this.form.submit();
        }
    },

    postSuccess: function(data) {
        if (!data.success) {
            return;
        }

        if (data.redirect_to) {
            window.location.href = data.redirect_to;
        }
    }
});

_.each($(".form-box"), function(item) {
    new Greenmine.GenericFormsView({el: $(item)});
});