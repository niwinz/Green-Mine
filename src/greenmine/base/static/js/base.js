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

/* Global gonway  module namespace. */

var Gonway = {};

Gonway.Form = Kaleidos.Form.extend({
    clear: function() {
        this.$("ul.errorlist").remove();
        this.$(".error-arrow-top").remove();

        if (this.globalErrorsBox) {
            this.globalErrorsBox.html("");
            this.globalErrorsBox.hide();
        }

        if (this.options.higlight) {
            this.$("." + this.options.higlight).removeClass(this.options.higlight);
        }
    },
    setErrorsFieldsStandatd: function(errors) {
        var self = this;

        _.each(errors.form, function(error_list, key) {
            var field = self.searchField(key);
            self.higlight(field);

            var error_list_dom = $(self.make('ul', {'class': 'errorlist', 'id': 'field-' + field.attr('id')}));
            var error_arrow_dom = $(self.make('div', {'class': 'error-arrow-top'}));

            _.each(error_list, function(item) {
                error_list_dom.append(self.make('li', {}, item));
            });

            error_arrow_dom.insertAfter(field);
            error_list_dom.insertAfter(field);
        });
    }
});

Gonway.MailboxModel = Backbone.Model.extend({
    defaults: {
        'messages': 2,
        'applications': 4
    },
    url: function() {
        return $(".navbar").attr('mailbox_update_url');
    }
});


/* Base view for all portlets.
 * Implements a server content loading on render method. */

Gonway.BasePortletView = Backbone.View.extend({
    render: function() {
        var self = this;
        $.get(self.$el.attr('url'), function(data) {
            self.$el.html(data);
            self.$el.slideDown(100, function() {
                self.trigger('ready');
            });
        });
    }
});


Gonway.HeaderView = Backbone.View.extend({
    el: $('.navbar'),

    events: {
        'click .mailbox': 'mailboxDropDown',
        'mouseleave .mailbox': 'mailboxSlideUp'
    },

    initialize: function() {
        _.bindAll(this,
            'mailboxDropDown',
            'mailboxSlideUp',
            'renderMailbox',
            'setProfileImage'
        );

        var self = this;

        /* Mailbox */
        //var update_url = this.$el.attr('mailbox_update_url');
        var mailbox_num_dom = this.$(".mailbox-num");

        this.mailbox = new Gonway.MailboxModel();
        this.mailbox.set("messages", mailbox_num_dom.attr('messages') || 0);
        this.mailbox.set("applications", mailbox_num_dom.attr('applications') || 0);

        /* Initial rendering of mailbox */
        this.renderMailbox();

        /* Update mailbox with server content every 2 seconds */
        //setInterval(function() {
        //    self.mailbox.fetch({success: self.renderMailbox});
        //}, 2000);
    },

    mailboxDropDown: function(e) {
        e.preventDefault();
        var target = $(e.currentTarget);
        target.css('border-color', '#FFFFFF');
        target.find('ul').slideDown();
    },

    mailboxSlideUp: function(e){
        var target = $(e.currentTarget);
        target.css('border-color', '#3D3B48');
        target.find('ul').fadeOut('fast');
    },

    renderMailbox: function() {
        var mailbox_num = this.$(".mailbox-num");
        mailbox_num.html(
            this.mailbox.get("messages") + this.mailbox.get("applications")
        );

        this.$(".mailbox-dropdown span.messages-num").html(this.mailbox.get('messages'));
        this.$(".mailbox-dropdown span.applications-num").html(this.mailbox.get('applications'));
    },

    setProfileImage: function(url) {
        this.$(".navbar-user a:first img").attr('src', url);
    }
});


Gonway.MainView = Backbone.View.extend ({
    el: $('body'),

    events: {
        "change .autocomplete-region": "countryChange"
    },

    initialize: function() {
        _.bindAll(this, 'reloadGraphs');
        this.reloadGraphs();
    },

    reloadGraphs: function() {
        var graphs = this.$('.canvas').not(".canvasReady");

        _.each(graphs, function(item) {
            var gitem = $(item);
            var width = gitem.attr('rel');

            /* The unique id is mandatory on canvas item */
            var graphId = gitem.attr('id');
            var graphSize = gitem.attr('size');
            var graphWidth = (graphSize / 100) * width;
            var graphColor = gitem.attr('color');
            var paper = Raphael(graphId, graphSize, 10);
            paper.rect(0, 0, graphSize, 10).attr({"font": '9px "Arial"', fill: "#ccc", "stroke-width": 0, r: "4px" });
            if(graphColor !== undefined){
                paper.rect(1, 1, graphWidth, 8).attr({"font": '9px "Arial"', fill: graphColor, "stroke-width": 0, r: "4px" });
            } else {
                paper.rect(1, 1, graphWidth, 8).attr({"font": '9px "Arial"', fill: "#4595DC", "stroke-width": 0, r: "4px" });
            }

            gitem.addClass("canvasReady");
        });
    },

    countryChange: function(event) {
        event.preventDefault();

        var target = $(event.currentTarget);
        var regionSelect = this.$(target.data('region-input'));
        var regionUrl = target.data('url');
        var self = this;

        $.get(regionUrl, {'country': target.val()}, function(data) {
            if (!data.success) return;
            regionSelect.html("");
            _.each(data.regions, function(region) {
                var optiondom = self.make('option', {'value': region.id}, region.name);
                regionSelect.append(optiondom);
            });
        }, 'json');
    }
});

Gonway.header = new Gonway.HeaderView();
Gonway.main = new Gonway.MainView();


/* Top Message framework */

Gonway.TopMessage = Backbone.Model.extend({
    level: function() {
        return this.get('level');
    },
    msg: function() {
        return this.get('msg');
    }
});

Gonway.TopMessageCollection = Backbone.Collection.extend({
    model: Gonway.TopMessage
});

Gonway.MessagesView = Backbone.View.extend({
    el: $("#top-message"),

    initialize: function() {
        _.bindAll(this);
        this.collection = new Gonway.TopMessageCollection();
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

Gonway.messages = new Gonway.MessagesView();
