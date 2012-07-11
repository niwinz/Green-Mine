Greenmine.SearchView = Backbone.View.extend({
    el: $(".search-form-box"),

    events: {
        'keypress #search-input': 'onKeyPress'
    },

    initialize: function() {
        _.bindAll(this, 'onKeyPress');
    },

    onKeyPress: function(event) {
        if (event.keyCode === 13) { // Press ENTER
            var url = this.$el.data('url');
            var q = $('#search-input').val();

            window.location = url + '?q=' + q;
        }
    },
});

Greenmine.searchView = new Greenmine.SearchView();
