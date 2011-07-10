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

var compact_db = function() {
    console.log('Not implemented');
}

var load_data = function(files) {
    files.forEach(function(file) {
        processess_file(file);
    });
}

var print_help = function() {
    console.log('Command: node bin/manage.js <option> [arg1[,argN]]');
    console.log('Options: compact_db, loaddata\n');
}

if (process.argv.length == 3){
    switch(process.argv[2]){
        case 'compact_db':
            compact_db();
            break;

        default:
            print_help();
    }
}
else if (process.argv.length > 3){
    switch(process.argv[2]){
        case 'loaddata':
            load_data(process.argv.slice(3));
            break
        default:
            print_help();
    }
}
else {
    print_help();
}
