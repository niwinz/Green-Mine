/* Messages fw, reimplemented in javascript from django 
 * Usage example:
 *      messages.info('Example info message');
 *      messages.error('Example error message');
 * */

//var removeErrors = function() {
//    $(".messages-container ul").hide(function() { $(this).find('li').remove(); });
//};
//
///* selector == 'div.messages-container' */
//var Messages = function(selector) {
//    this.active = false;
//    this.msgbox = $(selector);
//
//    if ( this.msgbox.length ){
//        this.active = true;
//    }
//    if (!this.msgbox.find('ul.messages').length) {
//        this.msgbox.append($('<ul class="messages" />'));
//        this.msgbox.find('ul.messages').hide();
//    }
//}
//
//Messages.prototype = {
//    reset: function(){
//        this.msgbox.find('ul.messages').html("");
//    },
//    _send: function(type, messagetext) {
//        if (! this.active ){
//            return null;
//        }
//        var msgdom = $('<li />').addClass(type).html(messagetext);
//        this.msgbox.find('ul.messages').append(msgdom);
//        this.msgbox.find('ul.messages').show();
//        setTimeout(removeErrors, 4000);
//    },
//    error: function(msg) {
//        this._send('error', msg);
//    },
//    info: function(msg) {
//        this._send('info', msg);
//    }
//};
//
//var messages = new Messages('div.messages-container');


var Messages = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
    },
    render: _.once(function() {
        if (this.$("ul.messages").length == 0) {
            $(this.el).append(this.make("ul", {class:"messages"}));
        }
    }),
    reset: function() {
        this.$("ul.messages").html("");
    },
    send: function(type, messagetext) {
        this.render();
        
        var msgdom = this.make("li", {class:type}, messagetext);
        this.$("ul.messages").append(msgdom);
        this.$("ul.messages").show();

        _.delay(this.removeErrors, 6000);
    },
    error: function(msg) {
        this.send("error", msg);
    },
    info: function(msg) {
        this.send("info", msg);
    },
    removeErrors: function() {
        this.$("ul.messages li").remove();
        this.$("ul.messages").hide()
    }
});

var messages = new Messages({el: $('div.messages-container')});
