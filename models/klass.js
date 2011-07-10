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
    _construct: function(name) {
        console.log("debug: ModelKlass constructor");
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
    }
});

/* Test only */
var User = Klass(ModelKlass,{
    _construct: function(name){
        this.name = name.toUpperCase();
    },
});
User.required = ['name'];

var b = new User('Andrei');
b.is_valid(function(valid, error) {
    console.log('debug:', valid, error);
});
