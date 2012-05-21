/*
 * Backbone-Form - Backbone form validator and ajax helper.
 *
 * This is a simple backbone form view for form validation
 * and ajax submit helper.
 *
 * Well integrated with django forms and django-superview
 * json output of form errors.
 *
 * Changelog:
 *  * 21-05-2012 - First public version. (0.1)
 *
 *
 * Author: Andrei Antoukh <andrei.antoukh@kaleidos.net>
 * License: BSD
 * Version: 0.1
*/

var Form = Backbone.View.extend({
    /* CONSTRUCTOR
     * 
     * This method by default need one parameter: `el`.
     * Aditionally, you can pass others:
     *
     *   `errors`
     *
     *      aditional errors messages.
     *
     *  `clearOnInit`
     *
     *      with this parameter to true, on create a form view instance
     *      clears all error list.
     *
     *  `resetOnInit`
     *      
     *      same as `clearOnInit` but reset form.
    */ 

    initialize: function() {
        _.bindAll(this, 'validate', 'clear', 'setErrors', 'collectData', 'submit',
                'success', 'error', 'reset', 'getXhr', 'fields', 'uploadProgress');

        if (this.options.clearOnInit) {
            this.clear();
        }

        if (this.options.resetOnInit) {
            this.reset();
        }

        this.default_errors = {
            'required': gettext('This field is required')
        };

        this.errors = {}

        
        _.extend(this.errors, this.default_errors)
        if (this.options.errors == undefined) {
            _.extend(this.errors, this.options.errors);
        }
    },
    
    /* 
     * Remove all errors on form.
    */

    clear: function() {
        this.$("ul.errorlist").remove();
    },

    /*
     * Reset a form. Remove all assigned values.
    */

    reset: function() {
        this.$("input[type=text], input[type=file], select, textarea").val('');
    },

    /* PRIVATE METHOD
     *
     * creates a custom XMLHttpRequest builder
     * TODO:  make this compatible with IE
    */
    
    getXhr: function() {
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener("progress", this.uploadProgress);
        return xhr;
    },

    /* PRIVATE METHOD
     *
     * Calculate a percentage of form upload progress and trigger `progress` 
     * event with a current percentaje.
    */

    uploadProgress: function(evt) {
        if (evt.lengthComputable) {
            this.bytesUploaded = evt.loaded;
            this.bytesTotal = evt.total;
            this.trigger('progress', Math.round(evt.loaded * 100 / evt.total));
        }
    },

    /* submit(opts):  Makes ajax submit of the asociated form
     * 
     * Posible params:
     *
     *   `success`:  
     *      
     *      this is a success callback, receives a response.  If this parameter 
     *      is undefined, fallback to use self implemented success method.
     *
     *   `error`
     *      
     *      same as `success` but for error.
     *
     *   `dataType`
     *      
     *      this is a jquery `dataType` parameter, by default is set to `json`.
     *
     *   `url`
     *      
     *      url to send a form data, by default is a form action.
     *
     *   `type` 
     *
     *      is a request type, by default, uses form type attribute.
     *
     *   `jqueryOpts`
     *
     *      with this parameter you can pass all jquery parametes ($.ajax()).
    */

    submit: function(opts) {
        if (opts === undefined) {
            opts = {};
        }

        var success = opts.success || this.success;
        var error = opts.error || this.error;
        var url = opts.url || this.$el.attr('action');
        var type = opts.type || this.$el.attr('type') || 'post';
        var dataType = opts.dataType || 'json';
        var enctype = opts.enctype || this.$el.attr('enctype') || false;
        var jquery_lowlevel_opts = opts.jqueryOpts || {};

        var ajax_params = {
            url: url,
            type: type,
            success: success,
            error: error,
            dataType: dataType,
            xhr: this.getXhr,
        };

        if (opts.data !== undefined) {
            ajax_params['data'] = opts.data;
        } else {
            ajax_params['data'] = this.collectData();
        }
        
        if (enctype && enctype == 'multipart/form-data') {
            ajax_params['processData'] = false;
            ajax_params['contentType'] = false;
        }

        _.extend(ajax_params, jquery_lowlevel_opts);
        return $.ajax(ajax_params);
    },

    /*
     * Fallback method for onsuccess submit.
    */

    success: function(data) {
        if (typeof data === "object" && data.errors && data.errors.form) {
            this.setErrors(this.errors.form);
        }
    },
    
    /* 
     * Fallback method for onerror submit 
    */

    error: function() {},
    
    /* collectData(opts)
     *
     * Collects form data. If form has attribute 'enctype' and is equal to 'multipart/form-data'
     * this method return FormData instance. If this interface is not found or is a normal form,
     * this internally use jquery.serialize() method.
     *
     * Options:
     *
     *  `forceSerialize`
     *
     *      with this parameter force user of jquery serialize on case if a form is multipart.
    */
    
    collectData: function(opts) {
        if (opts === undefined) { opts = {}; }
        if (opts.forceSerialize === undefined) { opts.forceSerialize = false; }
        
        if (this.$el.attr('enctype') === 'multipart/form-data' && !opts.forceSerialize) {
            return new FormData(this.el);
        } else {
            return this.$el.serialize();
        }
    },
    
    /* PRIVATE METHOD
     *
     * Return all fields on current associated form.
    */

    fields: function() {
        var _fields = new Array();
        _.each(this.$("input, select, textarea"), function(item) {
            _fields.push( $(item) );
        });

        return _fields;
    },
    
    /*
     * Validate with javascript some fields
     *
     * TODO: NOT IMPLEMENTED, UNDER DEVELOPMENT.
    */

    validate: function() {
        var required_fields = _.filter(this.fields(), function(item) {
            return item.attr('required') === 'true';
        });

        var errors = {};
        var has_errors = false;

        _.each(required_fields, function(item) {
            if (item.val() == "") {
                errors[item.attr('name')] = this.errors['required'];
                has_errors = true;
            }
        });
        
        if (has_errors) {
            this.setErrors(errors);
        }
        return has_errors;
    },

    /* setErrors(errors)
     *
     * Draw dinamicaly all errors returned by `render_json_error` from 
     * `django-superview`
     *
     * TODO: global form errors not implemented.
     * TODO: all errors to global option, not implemented.
    */

    setErrors: function(errors) {
        this.clear();
        var self = this;

        if (errors.form) {
            _.each(errors.form, function(error_list, key) {
                var field = self.$("#id_" + key);
                var error_list_dom = $(self.make('ul', {'class': 'errorlist', 'id': 'field-' + field.attr('id')}));

                _.each(error_list, function(item) {
                    error_list_dom.append(self.make('li', {}, item));
                });

                error_list_dom.insertBefore(field);
            });
        }
        
        if (errors.global) {
            // TODO
        }
    }
});

