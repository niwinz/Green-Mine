/* Author:
    RedDelicious
    Company: Kaleidos Open Source
*/

/* gettext dummy wrapper if not exists */

if (window.gettext === undefined) {
    window.gettext = function(text) {
        return text;
    };
}

if (window.interpolate === undefined) {
    window.interpolate = function(fmt, obj, named) {
        if (named) {
            return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
        } else {
            return fmt.replace(/%s/g, function(match){return String(obj.shift())});
        }
    };
}

jQuery.ajaxSettings.traditional = true;

$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

function getUrlVars(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function getIntListFromURLParam(param){
    var param_value = getUrlVars()[param];
    var return_list = [];
    if (param_value!== undefined){
        $.each(param_value.split(','), function(index, value){
            if (value!=''){
                return_list.push(parseInt(value));
            }
        });
    }
    return return_list;

}

function getStringListFromURLParam(param){
    var param_value = getUrlVars()[param];
    var return_list = [];
    if (param_value!== undefined){
        $.each(param_value.split(','), function(index, value){
            if (value!=''){
                return_list.push(value);
            }
        });
    }
    return return_list;

}


/* Top Message framework */

Greenmine.TopMessage = Backbone.Model.extend({
    level: function() {
        return this.get('level');
    },
    msg: function() {
        return this.get('msg');
    }
});

Greenmine.TopMessageCollection = Backbone.Collection.extend({
    model: Greenmine.TopMessage
});

Greenmine.MessagesView = Backbone.View.extend({
    el: $("#top-message"),

    initialize: function() {
        _.bindAll(this);
        this.collection = new Greenmine.TopMessageCollection();
        this.collection.on('reset', this.resetMessages);

        if (window.currentTopMessages !== undefined && window.currentTopMessages.length > 0){
            this.showMessages(window.currentTopMessages);
        }
    },

    showErrorMessages: function(messages) {
        var self = this;
        this.$el.html("");

        var error_messages_dom = $(this.make('ul', {'class': 'negative container'}));
        _.each(messages, function(item) {
            var message_item = self.make("li", {}, item);
            error_messages_dom.append(message_item);
        });

        this.$el.append(error_messages_dom);
        this.show();
    },

    showInfoMessages: function(messages) {
        var self = this;
        this.$el.html("");

        var info_messages_dom = $(this.make('ul', {'class': 'positive container'}));
        _.each(messages, function(item) {
            var message_item = self.make("li", {}, item);
            info_messages_dom.append(message_item);
        });

        this.$el.append(info_messages_dom);
        this.show();
    },

    resetMessages: function() {
        var self = this;
        this.$el.html("");

        var valid_messages = this.collection.filter(function(item) { return item.get('level') === 'valid'; });
        var error_messages = this.collection.filter(function(item) { return item.get('level') === 'error'; });


        if (valid_messages.length) {
            var valid_messages_dom = $(this.make('ul', {'class': 'positive container'}));
            _.each(valid_messages, function(item) {
                var message_item = self.make("li", {}, item.get('msg'));
                valid_messages_dom.append(message_item);
            });

            this.$el.append(valid_messages_dom);
        }

        if (error_messages.length) {
            var error_messages_dom = $(this.make('ul', {'class': 'negative container'}));
            _.each(error_messages, function(item) {
                var message_item = self.make("li", {}, item.get('msg'));
                error_messages_dom.append(message_item);
            });

            this.$el.append(error_messages_dom);
        }

        this.show();
    },

    show: function() {
        if (this.timeout !== undefined) {
            clearTimeout(this.timeout);
        }
        this.$el.show();

        this.timeout = setTimeout(this.hide, 6000);
    },

    hide: function() {
        this.$el.hide();
        this.timeout = undefined;
    },

    showMessages: function(messages) {
        this.collection.reset(messages);
    }
});

//Greenmine.messages = new Greenmine.MessagesView();
