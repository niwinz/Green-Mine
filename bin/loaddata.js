var settings = require('../settings');

var processess_file = function(filename){
    var docs = require(process.cwd() + '/' + filename);
    var db = settings.get_database();

    var notFoundCallback = function(obj) {
        db.save(obj, function(e, r){
            if(!e) { console.log('Inserting _design document: ', obj._id); }
            else { console.log('Error on insert _design document: ', obj._id); }
        });
    }

    var foundCallback = function(filedoc, dbdoc) {
        db.remove(dbdoc._id, dbdoc._rev, function(e, r){
            if(!e) { notFoundCallback(filedoc); }
            else { console.log('eeeee'); }
        });
    }

    docs.forEach(function(doc) {
        db.get(doc._id, function(e, r) {
            if (e) { notFoundCallback(doc); }
            else { foundCallback(doc, r); }
        });
    });
}

//console.log('Current directory: ' + process.cwd());

if (process.argv.length > 2){
    for(var i=2; i < process.argv.length; ++i) {
        processess_file(process.argv[i]);
    }
}
else {
    console.log('Invalid parameters...');
}
