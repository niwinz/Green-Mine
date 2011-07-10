module.exports = [
{
    _id:'_design/user',
    views: {
        all:{
            map: function(doc){
                if(doc.type == 'user'){
                    emit(doc.username, doc);
                }
            }
        }
    }
},
{
    _id:'_design/project',
    views: {
        /* Show all existing projects. */
        all: {
            map: function(doc) {
                if (doc.type == 'project') {
                    emit(doc.title, doc);
                }
            },
            reduce: function(keys, values) {
                return true;
            }
        },
        /* Search all projects for one user. 
         * help: key=username */
        on_user_exists: {
            map: function(doc) {
                if(doc.type == 'project') {
                    doc.users.forEach(function(item) {
                        emit(item, doc.title);
                    });
                }
            },
            reduce: function(keys, values){
                return values;
            }
        }
    }
}]

