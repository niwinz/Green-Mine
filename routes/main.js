module.exports = function(app){
    app.all(/.*/i, function(req, res, next) {
        console.log('app.all', req.url, req.method);
        next();
    });
    app.get('/', function(req, res) {
        res.send('Hello World');
    });
}
