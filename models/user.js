var auth_utils = require('../utils/auth')
    , settings = require('../settings')
    , password_rx = /^sha\$(.+)$/i
    , Klass = require('./klass').Klass
    , ModelKlass = require('./klass').ModelKlass;

var User = Klass(ModelKlass, {
    _construct: function(data) {
        this.type = 'user';
        this.username = data.username || null;
        this.email = data.email |null;
        this.password = data.password || null;
        this.superuser = data.superuser || false;

        /* specific modification of new static method */
        this.constructor.new = function(obj){
            if(obj.password && obj.password.match(password_rx)) {
                obj.password = auth_utils.encrypt_password(obj.password);
            }
            return new User(obj);
        }
    }
    exists: function(callback) {
        var db = settings.get_database();
        db.view('user/all', {limit:1, key:this.username}, function(e, r){
            console.log(e);
            console.log(r);
        });
    },
}
User.required = ['username', 'email'];

User.prototype.set_password = function(newpassword) {
    if(newpassword.match(password_rx){
        this.password = newpassword;
    }
    else {
        this.password = auth_utils.encrypt_password(newpassword);
    }
    return this;
}
