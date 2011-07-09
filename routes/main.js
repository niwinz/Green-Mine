module.exports = function(app){
    app.all(/.*/i, function(req, res, next) {
        console.log('app.all', req.url, req.method);
        next();
    });
    app.get('/', function(req, res) {
        res.redirect('/login');
    });
    app.get('/login', function(req, res) {
        res.render('login');
    });
}
