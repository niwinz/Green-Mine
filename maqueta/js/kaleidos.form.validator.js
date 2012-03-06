/* Kaleidos Form Validator.js 
 *
 * Copyright (c) 2011 Kaleidos <hello@kaleidos.net>
 * Copyright (c) 2011 Juan Francisco Alcántara <juanfran.alcantara@kaleidos.net>
 * Copyright (c) 2011 Andrei Antoukh <niwi@niwi.be>
 *
 * Dual licensed under the MIT or GPL Version 2 licenses.
*/

(function($){
    $.fn.validate = function(params) {
        var defaults = {
            validClass: 'valid-field',
            invalidClass: 'invalid-field',
            globalErrorObject: false,
            inlineErrors: true,
            formData: function() {
                return this.form.serialize();
            },
            validateOnchange: false,
            ajax: false,
            ajaxSuccess: function(data){
                if(data.submit){
                    self.form.data('ajax-valid', true);
                    self.form.submit();
                } else {
                    var errors = new Array(); 
                    for(var i=0; i<data.global.length; i++){
                        errors.push(data.global[i].error);
                    }
                    self.printGlobalErrors(errors);
                    
                    var field = 0;
                    for(var i=0; i<data.fields.length; i++){
                        field = self.elements.filter("[name="+data.fields[i].field+"]");
                        field.data('error', data.fields[i].msg);
                    }   
                    
                    self.printErrors();  
                }
            },
            presubmitValidation: false,
            onPrintError: function(){},
            globalErrorContainer: function(){
                if(!this.globalErrorObject){
                    var globalerror = $(document.createElement('div'))
                    .attr('class', 'global-error');
                    this.form.prepend(globalerror);
                    this.globalErrorObject = this.form.find('.global-error');
                }             
            },
            printGlobalErrors: function(errors){
                var html = '';
                for(var i=0; i<errors.length; i++){
                    html+= "<p>"+errors[i]+"</p>"
                }
                this.globalErrorContainer();     
                this.globalErrorObject.html("");
                this.globalErrorObject.append(html);             
            },
            printFieldGlobalError: function(text, id){
                this.removeGlobarError(id);
                this.globalErrorContainer();
                this.globalErrorObject.append("<p id='field-"+id+"'>"+text+"</p>");             
            },
            removeGlobarError: function(id){
                $("#field-"+id).remove();            
            },         
            printError: function(field){
                var error = field.data('error'); 
                $("#field-"+field.attr('id')).remove();
    
                if(error){
                    field.addClass(this.invalidClass);                
                    if(!this.disableInlineErrors){
                        if(this.inlineErrors){
                            $("<span class='field-error' id='field-"+field.attr('id')+"'>" + 
                                field.data('error')+"</span>").insertAfter(field);
                        }else{
                            this.printFieldGlobalError(field.data('error'), field.attr('id'));
                        }
                    }
                }else{
                    field.addClass(this.validClass);    
                }    
                this.onPrintError(field);         
            },
            printErrors: function(){
                for(var i=0; i<this.elements.length; i++){
                    this.printError($(this.elements[i]));
                }
            },
            submit: function(event){
                if(this.form.data('ajax-valid')){
                    return true;
                }
                valid = this.validate();
                this.printErrors();
                 
                if (this.presubmitValidation){
                    var valid2 = this.presubmitValidation();
                    if (valid) valid = valid2;
                }
                 
                if (!valid){
                    event.preventDefault();
                } else {
                    if (this.ajax){
                        event.preventDefault();
                        $.ajax({
                            dataType: 'json',
                            url: this.form.attr('action'),
                            type: this.form.attr('method'),
                            self: this,
                            data: this.formData(),
                            success: this.ajaxSuccess
                        });
                    }
                 }
            },
            validate: function(){
                 var valid = true;
                 for(var i=0; i<this.elements.length; i++){
                    if(!this.isValid($(this.elements[i]))){
                         valid = false;
                    }                 
                 }
    
                 return valid;
            },
            validateField: function(field){
                this.isValid(field);
                this.printError(field);
            },
            isValid: function(field){
                if (field.attr('type')=='submit'){
                    return true;
                } 
                 
                var valid = true; 
                var defaultmsgs = {
                    'required': 'Required.',
                    'email': 'Mail invalid'
                };
                
                if (this.errorsMsgs[field.attr('name')]!=undefined){
                    var msgs = $.extend(defaultmsgs, this.errorsMsgs[field.attr('name')]);
                } else {
                    var msgs = defaultmsgs;
                }
                
                field.data('error', false);
                
                if (field.attr('required')!=undefined){
                    if (field.attr('type')=='checkbox'){
                        if (!field.is(':checked')){
                            valid = false;
                            field.data('error', msgs.required);                        
                        }
                    } else {                
                        if ($.trim(field.val()).length==0){
                            valid = false;
                            field.data('error', msgs.required);
                        }
                    }
                }
    
                if (valid && field.attr('type')=='email'){
                    var email = /^([a-z0-9_\.\-\+]+)@([\da-z\.\-]+)\.([a-z\.]{2,6})$/i;
                    valid = email.test(field.val());
                    if (!valid)
                        field.data('error', msgs.email);
                }   
                
                if (this.customVal!=undefined){
                    if(valid && this.customVal[field.attr('name')]!=undefined){
                        valid = this.customVal[field.attr('name')](this, field);
                        if(!valid)field.data('error', msgs.custom);
                    }
                }
                return valid;
            },
            errorsMsgs: {},
            elements: new Array()
        };
         
        var self = $.extend(defaults, params);
    
        if ($(this).data('validator') !== undefined){
            self = $.extend($(this).data('validator'), self); 
        } else {
            self.elements = $(this).find('input,textarea,select');
             
            if (self.validateOnchange){
                self.elements.each(function(){
                    var bindevent = 'keyup';
                    if ($(this).attr('type') == 'checkbox'){
                        bindevent = 'change';
                    }
    
                    $(this).bind(bindevent, function(){
                       self.validateField($(this));
                    });            
                });
            }
            $(this).attr("novalidate", "novalidate")
                .bind("submit", function(event){ self.submit(event); });

            self.form = $(this);
            self.form.data('ajax-valid', false);
        }
         
        $(this).data('validator', self);
        return self;
    };  
})(jQuery);
