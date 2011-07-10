var uuid = require('node-uuid');
var auth_utils = require('../utils/auth');
var settings = require('../settings');

var password_rx = /^sha\$(.+)$/i;

var User = exports = module.exports = function(data) {
    data = data || {};
    this._id = data._id || null;
    this._rev = data._rev || null;
    this.type = 'user';
    this.username = data.username || null;
    this.email = data.email |null;
    this.password = data.password || null;
    this.superuser = data.superuser || false;
}

User.prototype.exists = function(callback) {
    var db = settings.get_database();
    db.view('user/all', {limit:1, key:this.username}, function(e, r){
        console.log(e);
        console.log(r);
    });
}
    
User.prototype.is_valid = function(callback) {
    if(!this.username) { return callback(new Error('username required')); }
    callback(null);
}

User.prototype.set_password = function(newpassword) {
    if(newpassword.match(password_rx){
        this.password = newpassword;
    }
    else {
        this.password = auth_utils.encrypt_password(newpassword);
    }
    return this;
}


/* Static methods */

exports.get = function(docorid, db, callback){
    var _id = null;
    if (typeof docorid == 'string'){ _id = docorid; }
    else { _id = docorid._id; }

    db.get(_id, function(err, doc){
        callback(err, new Post(doc));
    });
}

exports.new = function(descobject) {
    descobject._id = uuid();
    if(descobject.password && !descobject.password.match(password_rx)) { 
        descobject.password = auth_utils.encrypt_password(descobject.password);
    }
    return new Post(descobject);
}
