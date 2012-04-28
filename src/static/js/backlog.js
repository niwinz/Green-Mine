/* Models */
var UserStory = Backbone.Model.extend({
    defaults: {
        unassignUrl:""
    }
});

var UserStoryList = Backbone.Collection.extend({
    model: UserStory
});


var Milestone = Backbone.Model.extend({
    defaults: {
        title:"",
        dashboardUrl:"",
        assignUrl:"",
        userStories: new UserStoryList()
    }
});

var MilestoneList = Backbone.Collection.extend({
    model: Milestone
});


/* Views */

var MilestoneItemView = Backbone.View.extend({
    tagName: "div",
    initialize: function(){
        _.bindAll(this, 'render');
    },
    render: function(callback) {
        $.
    }
});
