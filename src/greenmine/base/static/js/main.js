function getUrlVars(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function getIntListFromURLParam(param){
    var param_value = getUrlVars()[param];
    var return_list = [];
    if (param_value!== undefined){
        $.each(param_value.split(','), function(index, value){
            if (value!=''){
                return_list.push(parseInt(value));
            }
        });
    }
    return return_list;

}

function getStringListFromURLParam(param){
    var param_value = getUrlVars()[param];
    var return_list = [];
    if (param_value!== undefined){
        $.each(param_value.split(','), function(index, value){
            if (value!=''){
                return_list.push(value);
            }
        });
    }
    return return_list;

}
