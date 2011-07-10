var cradle = require('cradle');

module.exports = {
    /* Constants */
    dbname: 'test2',
    dburl: 'http://localhost',
    dbport: 5984,
    dbsettings: {
        cache: true, 
        raw: false,
        auth: { 
            username: 'admin', 
            password: '123123' 
        }
    },

    /* Methods */
    get_database: function() {
        if (typeof this._connection == 'undefined'){
            this._connection = new(cradle.Connection)(this.dburl, this.dbport, this.dbsettings);
        }
        var database = this._connection.database(this.dbname);
        database.exists(function(err, value){
            if(!value && !err) { database.create(); }
        });
        return database;
    },
}
