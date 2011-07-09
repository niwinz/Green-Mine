
/**
 * Module dependencies.
 */

var express = require('express')
    , messages = require('express-messages');

var app = module.exports = express.createServer();

app.dynamicHelpers({
    messages: messages,
    glob: function(req){
        return {
            title: 'Green-Mine'
        }
    }
});

// Configuration

app.configure(function(){
    app.use(express.logger('\x1b[33m:method\x1b[0m \x1b[32m:url\x1b[0m :response-time'));
    app.set('views', __dirname + '/views');
    app.set('view engine', 'jade');
    app.use(express.bodyParser());
    app.use(express.methodOverride());
    app.use(express.cookieParser());
    app.use(express.session({ secret: 'your secret here' }));
    app.use(app.router);
    app.use(express.static(__dirname + '/public'));
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true })); 
});

app.configure('production', function(){
  app.use(express.errorHandler()); 
});

// Routes
require('./routes/main.js')(app);

app.listen(3000);
console.log("Express server listening on port http://localhost:%d in %s mode", app.address().port, app.settings.env);
