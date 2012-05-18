var UserStory = Backbone.Model.extend({});
var UserStoryCollection = Backbone.Collection.extend({
    model: UserStory
});


var UserStoryView = Backbone.View.extend({
    tagName: 'tr',

    events: {},

    initialize: function() {
        _.bindAll(this, 'render');
    },

    render: function() {
        this.$el.replaceWith(this.model.get('html'));
        return this;
    }
});


var DashboardView = Backbone.View.extend({
    el: $("#dashboard-matrix"),

    events: {},

    initialize: function() {
        _.bindAll(this, 'render', 'addOne', 'addAll');
        
        this.user_stories = new UserStoryCollection();
        this.user_stories.bind('add', this.addOne);
        this.user_stories.bind('reset', this.addAll);
        this.user_stories.fetch();
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

$(function() {
    var dashboard = new DashboardView();
});
