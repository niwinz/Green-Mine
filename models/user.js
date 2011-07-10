var uuid = require('node-uuid');
var auth_utils = require('../utils/auth');
var settings = require('../settings');

var User = exports = module.exports = function(data) {
    data = data || {};

    this._id = data._id || null;
    this._rev = data._rev || null;
    this.type = 'user';
    this.username = data.username || null;
    this.email = data.email |null;
    this.password = data.password || null;
}

User.prototype.exists = function(callback) {
    var db = settings.get_database();
    db.view('user/all', {limit:1, key:this.username}, function(e, r){});
}
    
User.prototype.is_valid = function(callback) {}


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
    return new Post(descobject);
}
