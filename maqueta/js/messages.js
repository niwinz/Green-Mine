/* Messages fw, reimplemented in javascript from django 
 * Usage example:
 *      messages.info('Example info message');
 *      messages.error('Example error message');
 * */

var removeErrors = function() {
    $(".messages-container ul li").hide(function() { $(this).remove(); });
};

/* selector == 'div.messages-container' */
var Messages = function(selector) {
    this.active = false;
    this.msgbox = $(selector);

    if ( this.msgbox.length ){
        this.active = true;
    }
}

Messages.prototype = {
    _send: function(type, messagetext) {
        if (! this.active ){
            return null;
        }
        var msgdom = $('<li />').addClass(type).html(messagetext);
        console.log(msgdom);
        this.msgbox.find('ul.messages').append(msgdom);
        setTimeout(removeErrors, 4000);
    },
    error: function(msg) {
        this._send('error', msg);
    },
    info: function(msg) {
        this._send('info', msg);
    }
};

var messages = new Messages('div.messages-container');
