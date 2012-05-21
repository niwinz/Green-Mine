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
        //var fd = new FormData();
        //fd.append("document", document.getElementById('id_document').files[0]);
        //fd.append("title", this.form.find('input[name=title]').val());
        
        var errors = this.form_view.validate();
        if (!errors) {
            var xhr = this.form_view.submit({success:this.uploadComplete});
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
