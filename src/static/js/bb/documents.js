var Form = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, 'validate', 'clear', 'setErrors', 'collect_data', 'submit',
                'success', 'error', 'getXhr', 'fields', 'uploadProgress');
        this.clear();
        this.has_files;

        this.default_errors = {
            'required': gettext('This field is required')
        };
    },

    clear: function() {
        this.$("ul.errorlist").remove();
        this.$("input[type=text], input[type=file], select, textarea").val('');
    },
    
    getXhr: function() {
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener("progress", this.uploadProgress);
        return xhr;
    },

    uploadProgress: function(evt) {
        if (evt.lengthComputable) {
            this.bytesUploaded = evt.loaded;
            this.bytesTotal = evt.total;
            this.trigger('progress', Math.round(evt.loaded * 100 / evt.total));
        }
    },

    submit: function(opts) {
        if (opts === undefined) {
            opts = {};
        }

        var success = opts.success || this.success;
        var error = opts.error || this.error;
        var url = opts.url || this.$el.attr('action');
        var type = opts.type || 'POST';
        var dataType = opts.dataType || 'json';

        var ajax_params = {
            url: url,
            type: type,
            success: success,
            error: error,
            dataType: dataType,
            xhr: this.getXhr,
        };

        if (opts.data === undefined) {
            ajax_params['data'] = this.collect_data();
        } else {
            ajax_params['data'] = opts.data;
        }
        
        if ((this.$el.attr('enctype') && this.$el.attr('enctype') == 'multipart/form-data' )|| this.has_files) {
            ajax_params['processData'] = false;
            ajax_params['contentType'] = false;
        }

        return $.ajax(ajax_params);
    },

    success: function(data) {
        if (typeof data === "object" && data.errors && data.errors.form) {
            this.setErrors(this.errors.form);
        }
    },

    error: function() {},

    collect_data: function() {
        var data = {};
        this.has_files = false;

        _.each(this.fields(), function(item) {
            var item = $(item);
            var item_type = item.attr('type');

            if (item_type === 'submit' || item_type == 'button') return;
            else if (item_type == 'file') this.has_files = true;
            
            data[item.attr('name')] = item.val();
        });

        if (this.has_files) {
            var new_data = new FormData();

            _.each(data, function(value, key) {
                new_data.append(key, value);
            });

            data = new_data;
        }
        return data;
    },

    fields: function() {
        var _fields = new Array();
        _.each(this.$("input, select, textarea"), function(item) {
            _fields.push( $(item) );
        });

        return _fields;
    },
        
    validate: function() {
        var required_fields = _.filter(this.fields(), function(item) {
            return item.attr('required') === 'true';
        });

        var errors = {};
        var has_errors = false;

        _.each(required_fields, function(item) {
            if (item.val() == "") {
                errors[item.attr('name')] = this.default_errors['required'];
                has_errors = true;
            }
        });
        
        if (has_errors) {
            this.setErrors(errors);
        }
        return has_errors;
    },

    setErrors: function(errors) {
        this.clear();
        var self = this;

        _.each(errors, function(error_list, key) {
            var field = self.$("#id_" + key);
            var error_list_dom = $(self.make('ul', {'class': 'errorlist', 'id': 'field-' + field.attr('id')}));

            _.each(error_list, function(item) {
                error_list_dom.append(self.make('li', {}, item));
            });

            error_list_dom.insertBefore(field);
        });
    }
});

var UploadDialog = Backbone.View.extend({
    events: {
        'submit form': 'onUploadFileClick',
        'change #id_document': 'onFileSelected',
    },

    initialize: function() {
        _.bindAll(this, 'onColorboxClose', 'clear', 'show', 'onUploadFileClick', 'uploadComplete');

        this.form = this.$("form");
        this.form_view = new Form({el: this.form});
        this.file_selected = false;
    },

    clear: function() {
        this.form_view.clear();
        
        this.$("#fileName, #fileSize, #fileType").html("");
        this.$("#fileInfo").hide();
        this.$("#progressBar").css({'display':'none', 'width': '0px'});
    },

    onFileSelected: function(event) {
        var file = this.$("#id_document").prop('files')[0];
        var fileSize = 0;

        if (file.size > 1024 * 1024) {
            fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
        } else {
            fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';
        }
        
        this.$("#fileInfo").show();
        this.$("#fileName").html("Name: " + file.name);
        this.$("#fileSize").html("Size: " + fileSize);
        this.$("#fileType").html("Type: " + file.type);

        $.colorbox.resize();
        this.file_selected = true;
    },

    onUploadFileClick: function(event) {
        event.preventDefault();

        this.$("#uploadResponse").hide();
        this.$("#progressNumber").html("");

        // Collect data
        var fd = new FormData();
        fd.append("document", document.getElementById('id_document').files[0]);
        fd.append("title", this.form.find('input[name=title]').val());
        
        var errors = this.form_view.validate();
        if (!errors) {
            var xhr = this.form_view.submit({data:fd, success:this.uploadComplete});
        }
    },

    uploadComplete: function(data) {
        if (data.success) {

            this.form_view.clear()
            $.colorbox.close();
            this.file_selected = false;
        } else {
            this.form_view.setErrors(data.errors.form);
            $.colorbox.resize();
        }
        
        if (data.html) {
            $(data.html).insertAfter($(".documents-table .head-row"));
        }
    },

    show: function(target) {
        this.$el.removeClass('hidden');
        this.clear();
        
        target.colorbox({
            inline:true, 
            width:'400px',
            onCleanup: this.onColorboxClose,
        });
    },

    onColorboxClose: function() {
        this.$el.addClass('hidden');
    }
});

var DocumentsView = Backbone.View.extend({
    el: $("#documents-dashboard"),

    events: {
        "click .context-menu .new-document": "onUploadDocumentClick",
        "click .document-row .metaicon img.delete": "onDeleteDocumentClick"
    },

    initialize: function() {
        _.bindAll(this, 'onUploadDocumentClick', 'onDeleteDocumentClick');
        this.dialog = new UploadDialog({el: $("#upload-dialog"), target: self});
    },

    onUploadDocumentClick: function(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        this.dialog.show(target);
    },
    onDeleteDocumentClick: function(event) {
        event.preventDefault();
        var self = $(event.currentTarget);

        var buttons = {};
        buttons[gettext('Delete')] = function() {
            $(this).dialog('close');
            $.post(self.attr('deleteurl'), {}, function(data) {
                self.closest('.document-row').remove();
            });
        };

        buttons[gettext('Cancel')] = function() {
            $(this).dialog('close');
        };

        $(".delete-document-dialog").dialog({
            modal: true,
            width: '220px',
            buttons: buttons
        });
    }
});

$(function() {
    var documents = new DocumentsView();
});
