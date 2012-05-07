(function($){
    $( ".datepicker, #id_finish_date, #id_estimated_finish" ).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "mm/dd/yy"
    });
})(jQuery);


var milestone_dashboard_bindings = function() {
    $('.user-story .user-story-status .user-story-task').live('mouseenter', function(e) {
        if(!$(this).is(':data(draggable)')) {
            $(this).draggable({ handle: '.user-story-task', revert: 'invalid', helper:'clone' });
            $(this).draggable();
            apply_dropable_bindings();
        }
    });

    var update_progress = function() {
        var stats_url = $("#progress-bar").attr('rel');
        $.get(stats_url, function(data){
            if (data.valid) { $("#progress-bar").progressbar('option', 'value', data.v); }
        }, 'json');
    };
    update_progress();

    var apply_dropable_bindings = function() {
        $('.user-story .user-story-status').each(function(idx, element) {
            var self = $(this);
            $(element).droppable({
                activeClass: 'add',
                tolerance: 'pointer',
                hoverClass: "ui-state-active",
                drop: function(event, ui) {
                    var params = {
                        modify_flag: self.attr('rel'),
                        us : self.parents('.user-story').attr('us'),
                        milestone: $(ui.draggable).attr('ml')
                    }
                    var mod_url = $(ui.draggable).attr('url');
                    $.ajax({
                        url:mod_url, 
                        data:params,
                        type: 'POST',
                        dataType:'json',
                        success: function(data){
                            if (data.valid) {
                                self.append($(ui.draggable).clone());
                                $(ui.draggable).remove();
                                ui.draggable.draggable('option','revert', false);
                                update_progress();
                            }
                        },
                        error: function() {
                            ui.draggable.draggable('option','revert', true);
                        }
                    });
                }
            });
        });
    };

    $(".user-story .user-story-task .participants").live('change', function(e) {
        var self = $(this);
        $.get(self.attr('url'), {userid: self.val()}, function(data) {
        }, 'json');
    });

    /* Set progress bar */
    $('#progress-bar').progressbar();
}


/*
 * Print errors like django forms.
*/

var djangoPrintError = function (self, field){
    var error = field.data('error'); 
    $("#field-" + field.attr('id')).remove();
    if (error) {
        field.addClass(this.invalidClass);                
        if(!self.disableInlineErrors) {
            if(self.inlineErrors) {
                $("<ul class='errorlist' id='field-"+field.attr('id')+"'><li>" + 
                    field.data('error') + "</li></ul>").insertBefore(field);
            } else {
                self.printFieldGlobalError(field.data('error'), field.attr('id'));
            }
        }
    } else {
        field.addClass(self.validClass);    
    }    
    self.onPrintError(field);      
}


/*
 * On submit succes, print error messages or redirect.
*/

var djangoAjaxSuccess = function(self, data) {
    if (data.messages !== undefined){
        messages.reset();
        messages._send(data.messages.type, data.messages.msg);
    }
    
    if (data.valid) {
        self.form.data('ajax-valid', true);

        if (data.redirect_to !== undefined){
            window.location.href = data.redirect_to;  
        } 
    } else {
        jQuery.each(data.errors, function(index, value){
            field = self.elements.filter("[name="+index+"]");
            field.data('error', value[0]);
        })    
        self.printErrors();
    }
}

$(document).ready(function(){
    if ($('#milestone-dashboard').length) {
        milestone_dashboard_bindings();
    }

    if ($('#us-module').length){
        milestone_dashboard_bindings();
    }

    if ($("#login-form").length) {
        $("#id_username").focus();
        $("#login-form").validate({
            printFieldError: function(field) {
                djangoPrintError(this, $(field));
            },
            ajax: true,
            ajaxSuccess: function(data) {
                djangoAjaxSuccess(this.self, data);
            }
        });
    }
    
    if ($("#forgotten-password-form").length) {
        $("#id_email").focus();
        $("#forgotten-password-form").validate({
            errorsMsgs: {
                email: {username: gettext('Required.')}
            },
            printFieldError: function(field) {
                djangoPrintError(this, $(field));
            },
            ajax: true,
            ajaxSuccess: function(data) {
                djangoAjaxSuccess(this.self, data);
            }
        });
    }
    
    if ($("#new-project-form, #edit-project-form").length) {
        $("#new-project-form, #edit-project-form").validate({
            printFieldError: function(field) {
                djangoPrintError(this, $(field));
            },
            ajax: true,
            ajaxSuccess: function(data) {
                djangoAjaxSuccess(this.self, data);
            },
            customValidation: {
                username: function(self, field) {
                    if ($(".users-added tr").length>1) {
                        return true;
                    } else {
                        messages.reset();
                        messages._send('error', gettext('You must specify at least one person to the project'));
                        return false;
                    }
                }
            }           
        });          
    }    

    if($('#projects').length){
        $('.table01 a.delete').click(function(e){
            var self = $(this);
            //self.closest('.un-us-item').css('border', '1px solid red');
            
            var buttons = {};
            buttons[gettext('Delete')] = function() {
                var $this = $(this);
                $.post(self.attr('rel'), {}, function(data) {
                    $this.dialog('close');
                    self.parents('tr').remove();
                });
            };
            buttons[gettext('Cancel')] = function() {
                $(this).dialog('close');
            };

            $(".delete-project-dialog").dialog({
                modal: true,
                width: '220px',
                buttons: buttons
            });

            e.preventDefault();
        });
        
        $("#open-import-project").click(function(e){
            e.preventDefault();
            $("#import-project").slideToggle("slow");
        })
    }

    if($("#project").length){
        $("input.user-autocomplete").autocomplete({
            minLength: 1,
            select: function(event, ui) {
                var currentuser_dom = $("input.user-autocomplete").parent().find("input.user-currentvalue");
                currentuser_dom.val(ui.item.id);
                currentuser_dom.attr('name', ui.item.value);
                currentuser_dom.attr('gravatar', ui.item.gravatar);
            },
            source: function(request, response) {
                var url = $("input.user-autocomplete").attr('link');
                url = url + "?term=" + request.term;
                $.get(url,  function(data) {
                    if (data.valid){response(data.list);}
                }, 'json');
            }
        });
        
        $("#btn-usr-project").click(function(e){
            var role = $(".users-roles [name='rol-aux']");
            if (role.val().length == 0){
                alert("Selecciona un rol");
            } else {
                var user = $("input.user-autocomplete").parent().find("input.user-currentvalue");
                if (user.val().length){
                    if($("#user-project tbody").find('input[name="user_' + user.val() + '"]').length < 1){
                        var html = "<tr>" +
                            '<td><img width="30" src="'+ user.attr('gravatar') +'">' + user.attr('name') + '</td>' +
                            '<td>'+role.find('option:selected').html()+'</td>' +
                            '<td><a class="delete" rel="' + user.val() + '" href="">Borrar</a></td>' +
                            '<input type="hidden" name="user_' + user.val() + '" value="' + role.val() + '" /></tr>';
                        $("#user-project tbody").append(html);
                        $("input.user-autocomplete").val("");
                    }
                }
            }
            e.preventDefault();
        });
        $("#user-project").delegate('a.delete', 'click', function(event){
            $(this).parents('tr').remove();
            event.preventDefault();
        });        
    }
    
    if($("#issue").length){
        $("#issue").delegate(".delete-user", "click", function(e){
            $(this).parent().fadeOut("400", function(){  
                var realinput = $(this).parent().find("input[type='hidden']");
                if($(realinput).val().length){    
                    var values = $(realinput).val().split(',');
                    values.splice(jQuery.inArray($(this).attr('rel'),values),1);
                    $(realinput).val(values.join(','));
                }else{
                    $(realinput).val($(this).attr('rel'));
                }
                $(this).remove();
            });
            e.preventDefault();
        })
        
        $("input.users-autocomplete").autocomplete({
            minLength: 1,            
            select: function(event, ui) {
                var realinput = $(this).parent().find("input[type='hidden']");     
                var values = $(realinput).val().split(',');     
                if(jQuery.inArray(ui.item.id,values)==-1){
                    values.push(ui.item.id)
                    if($(realinput).val().length){    
                        $(realinput).val(values.join(','));
                    }else{
                        $(realinput).val(ui.item.id);
                    }
                    var html = "<span rel='"+ui.item.id+"' class='delete-user-ac'>"+ui.item.label+"<a class='delete-user' href=''></a></span>";
                    $(this).parent().append(html);
                }
                $(this).val("");    
                return false;
            },
            source: function(request, response) {
                var url = $("input.user-autocomplete").attr('urlautocomplete');
                url = url + "?term=" + request.term;
                $.get(url,  function(data) {
                    if (data.valid){response(data.list);}
                }, 'json');
            }
        });   
        
        $("input.user-autocomplete").autocomplete({
            minLength: 1,            
            source: function(request, response) {
                var url = $("input.user-autocomplete").attr('urlautocomplete');
                url = url + "?term=" + request.term;
                $.get(url,  function(data) {
                    if (data.valid){response(data.list);}
                }, 'json');
            }
        }); 
        
        $("#issue").delegate(".delete-file", "click", function(e){
            $(this).parent().fadeOut("400", function(){  
                var realinput = $("#input-delete-files");
                if($(realinput).val().length){
                    var values = $(realinput).val().split(',');
                    values.push($(this).attr('rel'));
                    $(realinput).val(values.join(','));
                }else{
                    $(realinput).val($(this).attr('rel'));
                }
                $(this).remove();
            });
            e.preventDefault();
        })     
    }
    
    if ($("#dashboard").length) {        
        (function($) {
            var dragAndDrop = function() {
                $("#bin").droppable({activeClass: 'bin2',  tolerance: 'pointer', 
                drop: function(ev, ui){
                    /* Drop ¿Que? Milestone? */
                    if($(ui.draggable).hasClass('milestone')){
                        var data = {};
                        $.ajax({url : '', type : 'POST', data: data});
                    }

                    /* Drop task */
                    else if($(ui.draggable).hasClass('task')){
                        var issue_drop_url = $(ui.draggable).data('drop_url');
                        $.post(issue_drop_url, function(data) {
                            if (data.valid) {
                                var old_milestone = $("#milestones .selected");

                                if($(ui.draggable).data('status')=='fixed'){
                                    $(old_milestone).data('completed_tasks', parseInt($(old_milestone).data('completed_tasks'))-1);
                                }

                                $(old_milestone).data('total_tasks', parseInt($(old_milestone).data('total_tasks'))-1);
                                $(old_milestone).updateHtml();
                            }
                        }, 'json');
                    }
                    $(ui.draggable).remove();
                }});

                $('#tasks').delegate('li', 'mouseenter', function() {
                    if(!$(this).is(':data(draggable)')) {
                        $(this).draggable({handle:'.dg', helper: 'clone', cursorAt: {cursor: "crosshair", top: -5, left: -5}, revert: 'invalid'});        
                    }
                    var milestones = $("li.milestone");
                    var milestones_length = milestones.length;
                    for(var i=0; i<milestones_length; i++){
                        if(!$(milestones[i]).is(':data(droppable)')) {
                            $(milestones[i]).droppable({activeClass: 'add',  tolerance: 'pointer', 
                            drop: function(ev, ui){
                                ui.draggable.draggable('option','revert',false);
                                if(!$(this).hasClass('selected')){
                                    var issue_asociate_url = $(ui.draggable).data('asociate_url');
                                    var milestone_id = $(this).data('id');
                                    var self = $(this);

                                    var params = {milestone:milestone_id};
                                    $.get(issue_asociate_url, params, function(data){
                                        if (data.valid) {
                                            var old_milestone = $("#milestones .selected");
                                            if($(ui.draggable).data('status')=='fixed'){
                                                self.data('completed_tasks', parseInt(self.data('completed_tasks'))+1);
                                                $(old_milestone).data('completed_tasks', parseInt($(old_milestone).data('completed_tasks'))-1);
                                            }
                                            self.data('total_tasks', parseInt(self.data('total_tasks'))+1);
                                            $(old_milestone).data('total_tasks', parseInt($(old_milestone).data('total_tasks'))-1);
                                            self.updateHtml(); 
                                            $(old_milestone).updateHtml(); 
                                            $(ui.draggable).remove();
                                        }
                                    }, 'json');
                                } else {
                                    ui.draggable.draggable('option','revert',true);
                                }
                            }
                            });
                        }
                    }
                });                     
            }
            
            /*
             * TODO: areglar esta funcion, ya que no hace su trabajo
             */
            var filters = function(){
                //$("#tasks-filters select").val(-1);
                $("#tasks-filters").delegate("select", "change", function(){
                    var selects = $("#tasks-filters select");
                    var lis = $("#tasks li");
                    $(lis).hide();
                    $(lis).filter(function() {
                        var show = true;
                        var ln = selects.length;

                        for(var i=0; i<ln; i++){
                            if($(selects[i]).val()!=""){
                                if($(this).data($(selects[i]).attr("name"))!=$(selects[i]).val()){
                                    show = false;
                                    break;
                                }
                            }
                        }
                        return show;
                    }).show();
                });
            };
                        
            //init dashboard
            //milestones_bindings();
            dragAndDrop();
            //filters();   
        })(jQuery);
    }
    
    
    $(".file").live("change", function(e){
        if(!$(this).attr('rel')){
            $(this).parent().append('<input type="file" class="file ">');
            $(this).attr('rel', 1);
        }
    });
});

function subClass() {
    this.inheritFrom = superClass;
    this.inheritFrom();
    this.subtest = subTest; //attach method subTest
}
