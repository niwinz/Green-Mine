var uuid = require('node-uuid');

var Klass = function(Parent, props){
    var Child = function() {
        if (Child._super && Child._super.hasOwnProperty('_construct')) {
            Child._super._construct.apply(this, arguments);
        }

        if(Child.prototype.hasOwnProperty('_construct')) {
            Child.prototype._construct.apply(this, arguments);
        }
    };

    Parent = Parent || Object;

    var F = function() {}
    F.prototype = Parent.prototype;
    Child.prototype = new F();
    Child._super = Parent.prototype;
    Child.prototype.constructor = Child;

    var i;
    for (i in props){
        if (props.hasOwnProperty(i)) {
            Child.prototype[i] = props[i];
        }
    }
    return Child;
}


var ModelKlass = Klass(null, {
    _construct: function(obj) {
        var self = this;
        this._id = obj._id || uuid();
        this._rev = obj._rev || null;
        this.constructor.new = function(data) {
            return new self.constructor(data);
        }
        this.constructor.get = function(doc, db, callback) {
            /* TODO: add _rev optional parameter */
            var objid = null;
            if(typeof doc == 'string') { objid = doc; }
            else { objid = doc._id; }

            db.get(objid, function(err, doc) {
                callback(err, new self.constructor(doc));
            });
        }
    },
    is_valid: function(callback) {
        if (!this.constructor.required){ 
            return callback(true, null); 
        }
        else if (this.constructor.required.length < 1){ 
            return callback(true, null); 
        }

        var i = 0, req = this.constructor.required;
        for(i=0; i < req.length; ++i) {
            if(!this[req[i]]) { 
                return callback(false, new Error(this[req[i]] + " required")); 
            }
        }
        callback(true, null);
    },
    _save: function(){
        var copy = {};
        for (var attr in this) {
            if (this.hasOwnProperty(attr) && attr != '_id' && attr != '_rev') {
                copy[attr] = this[attr];
            }
        }
        return copy;
    },
    save: function(db, callback) {
        var self = this;
        var save_callback = function(err, res) {
            if(!err){
                self._id = res.id;
                self._rev = res.rev;
            }
            callback(err, res, self);
        }

        if (self._rev) {
            db.save(self._id, self._rev, self._save(), save_callback);
        }
        else {
            db.save(self._id, self._save(), save_callback);
        }
    }
});

/* Test only */
//var User = Klass(ModelKlass,{
//    _construct: function(obj){
//        this.name = obj.name || 'Ana';
//    },
//});
//User.required = ['name'];
//
//var b = new User('Andrei');
//b.is_valid(function(valid, error) {
//    console.log('debug:', valid, error);
//});
