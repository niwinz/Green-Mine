(function($){
    $( ".datepicker, #id_finish_date" ).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "dd/mm/yy"
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

    $("#new-us").click(function(e) {
        if (!$('#form-inserts').data('edit')) {
            $('#form-inserts').data('edit', true);
            $('#form-inserts #us-lb, #form-inserts').removeClass('hidden');
            
            var form = $("#form-inserts #us-lb form");
            $(form).each (function() {this.reset();});
        }
        e.preventDefault();
    });

    $("#new-task").click(function(e) {
        if (!$('#form-inserts').data('edit')) {
            $('#form-inserts').data('edit', true);
            $('#form-inserts #task-lb, #form-inserts').removeClass('hidden');

            var form = $("#form-inserts #task-lb form");
            $(form).each (function() {this.reset();});
            if ($(form).data('us_id')) { $(form).find('#id_us').val($(form).data('us_id')); }
        }
        e.preventDefault();
    });

    $('#form-inserts .lb .cancel').click(function(e) {
        $('#form-inserts .lb, #form-inserts').addClass('hidden');
        $('#form-inserts').data('edit', false);
        e.preventDefault();
    });

    formUtils.ajax("#us-lb form", function(data, form){
        if(data.valid){
            $('#user-stories-module').append($(data.html));
        }
        $('#form-inserts #us-lb, #form-inserts').addClass('hidden');
    });

    formUtils.ajax("#task-lb form", function(data, form){
        if(data.valid){
            var html = $(data.html);
            $("#us" + data.us + " .status-new").append(html);
            $('#form-inserts #task-lb, #form-inserts').addClass('hidden');
        }
    });

    $(".user-story .user-story-header a.add-task").live('click', function(e) {
        var usid = $(this).parents('.user-story').attr('us');
        $("#form-inserts #task-lb form").data('us_id', usid);
        $(document).scrollTop(50);
        $("#new-task").trigger('click');

        e.preventDefault();
    });

    $(".user-story .user-story-header a.remove-us").live('click', function(e) {
        // TODO
        e.preventDefault();
    });

    $(".user-story .user-story-task .participants").live('change', function(e) {
        var self = $(this);
        $.get(self.attr('url'), {userid: self.val()}, function(data) {
        }, 'json');
    });

    /* Set progress bar */
    $('#progress-bar').progressbar();
}

$(document).ready(function(){
    $(".validate").validate();
    
    if ($('#milestone-dashboard').length) {
        milestone_dashboard_bindings();
    }

    if ($('#us-module').length){
        milestone_dashboard_bindings();
    }
    
    if($("#login-form").length){
		$("#id_username").focus();
        formUtils.ajax("#login-form", function(data){
            if(data.redirect_to) location.href = data.redirect_to;
        });
        
        formUtils.ajax("#forgotten-password-form", function(data){
            
        });        
        
        $("#open-forgotten-password-form").click(function(e){
            $("#login-form").fadeOut("fast", function() {
                $("#forgotten-password-form").fadeIn("fast");
            });
            e.preventDefault();
        });   
    
        $("#close-forgotten-password-form").click(function(e){
            $("#forgotten-password-form").fadeOut("fast", function() {
                $("#login-form").fadeIn("fast");
            });
            e.preventDefault();
        });
    }

    if($('#projects').length){
        $('.table01 a.delete').click(function(e){
            var self = $(this);
            $.post($(this).attr('rel'), function(data){
                self.parents('tr').remove();
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
            var roles = $("#edit-profile-form [name='rol-aux']:checked");
            if (roles.length == 0){
                alert("Selecciona un rol");
            } else {
                var user = $("input.user-autocomplete").parent().find("input.user-currentvalue");
                if (user.val().length){
                    if($("#user-project tbody").find('input[name="user_' + user.val() + '"]').length < 1){
                        var html = "<tr>" +
                            '<td><img width="30" src="'+ user.attr('gravatar') +'">' + user.attr('name') + '</td>' +
                            '<td>'+$(roles[0]).attr('rolname')+'</td>' +
                            '<td><a class="delete" rel="' + user.val() + '" href="">Borrar</a></td>' +
                            '<input type="hidden" name="user_' + user.val() + '" value="' + $(roles[0]).val() + '" /></tr>';
                        $("#user-project tbody").append(html);
                        $("#user-project tbody").find("a.delete").click(function(event){
                            $(this).parents('tr').remove();
                            event.preventDefault();
                        });
                        $("input.user-autocomplete").val("");
                    }
                }
            }
            e.preventDefault();
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
        function Dashboard() {  
            $.fn.updateHtml = function() {
                if ($(this).hasClass('milestone')) {
                    $(this).html(milestoneHtml($(this).data()));
                } else {
                    if ($(this).hasClass('task')) {
                        $(this).html(taskHtml($(this).data()));
                    }
                }
            };                
            
            function milestoneHtml(ml) {
                var html =  '<div class="ml"><span class="name">' + ml.name + '</span><div>';
                if (ml.id) {
                     html += '<span class="estimated_finish">' + ml.estimated_finish + '</span>';
                }
                html += '</div></div>';
                if (ml.id) {
                    html += '<a href="" class="edit"></a><a href="' + ml.detail_url + '" class="detail-ml"></a>';
                }
                return html;
            }
            
            function taskHtml(tk) {
                var html = '<div class="dg">%s<span>[ Estado: %s | Prioridad: %s ]</span></div>'
                    + '<a class="edit" href=""></a><a href="%s" class="detail"></a>';
                return interpolate(html, [tk.subject,tk.status_view,tk.priority_view,tk.url]);
            }            
            
            function loadTasks(url) {
                $("#tasks").hide();

                $.get(url, function(data) {
                    var tkul = $("#tasks");
                    $(tkul).html("");
                    ln = data.tasks.length; 
                    var tks = data.tasks;
                    
                    for(var i=0; i<ln; i++){
                        var item = $("<li/>")
                            .addClass('task')
                            .data(tks[i])
                            .html(taskHtml(tks[i]))
                            .appendTo(tkul); 
                    }
                    $(tkul).show();
                }, 'json');
            }

            var load_milestones = function() {
                var milestones_req_url = $("#dashboard").attr("rel");
                $.get(milestones_req_url, function(data) {
                    var ln = data.milestones.length;
                    var ml = data.milestones;
                    var li = new Array();

                    for(var i=0; i<ln; i++){
                        li.push($("<li>").addClass('milestone').html(milestoneHtml(ml[i])).data(ml[i]));    
                    }
                   
                    loadTasks($(li[0]).data().url);
                    $(li[0]).addClass('selected');
                    
                    var mlul = $("#milestones");
                    mlul.html('');

                    $(li).each(function(){
                        $(mlul).append(this);
                    })
                }, 'json');
            };

            var milestones_bindings = function() {
                $("#milestones").delegate(".ml", "click", function(e){
                    $("#tasks-filters select").val(-1);
                    $("#milestones").find(".selected").removeClass("selected");
                    var li = $(this).parent()
                    $(li).addClass("selected");
                    loadTasks($(li).data("url"))
                });
                load_milestones();
            };
            
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

            var hide_forms = function() {
                $('#form-inserts .lb, #form-inserts').addClass('hidden');
                $('#form-inserts').data('edit', false);
            };

            var formsBindings = function() {
                var edit = null;

                $("#new-milestone").click(function(e) {
                    e.preventDefault();
                });
                $("#new-issue").click(function(e) {
                    if (!$('#form-inserts').data('edit')) {
                        $('#form-inserts').data('edit', true);
                        $('#form-inserts #issue-lb, #form-inserts').removeClass('hidden');
                        
                        var form = $("#form-inserts #issue-lb form");
                        $(form).each (function() {this.reset();});
                        $(form).attr('action', $(form).attr('newaction'));
                        $(form).attr('rel', 'new');
                    }
                    e.preventDefault();
                });

                $('#new-milestone').click(function(e) {
                    if (!$('#form-inserts').data('edit')) {
                        $('#form-inserts').data('edit', true);
                        $('#form-inserts #milestone-lb, #form-inserts').removeClass('hidden');
                        
                        var form = $("#form-inserts #milestone-lb form");
                        $(form).each (function() {this.reset();});
                        $(form).attr('action', $(form).attr('newaction'));
                        $(form).attr('rel', 'new');
                    }
                    e.preventDefault();
                });

                /* Cancel button bindings */
                $('#form-inserts .lb .cancel').click(function(e) {
                    hide_forms();
                    e.preventDefault();
                });

                $("#milestones").delegate(".edit", "click", function(e){
                    edit = $(this).parent();
                    var form = $("#milestone-lb form");
                    
                    $(form).each (function() {this.reset();});
                    $(form).attr('action', $(edit).data('edit_url'));
                    $(form).attr('rel', 'edit');
                    //milestoneform.reset();

                    $.each($(edit).data(), function(key, value) { 
                        $(form).find("[name='"+key+"']").val(value);
                    });

                    $('#form-inserts #milestone-lb, #form-inserts').removeClass('hidden');
                    e.preventDefault();
                });
                
                $("#tasks").delegate(".edit", "click", function(e){
                    edit = $(this).parent();
                    var form = $("#issue-lb form");
                    $(form).each (function() {this.reset();});
                    $(form).attr('action', $(edit).data('edit_url'));
                    $(form).attr('rel', 'edit');
                    
                    issueform.resetForm(); 
                    $.each($(edit).data(), function(key, value) { 
                       $(form).find("[name='"+key+"']").val(value);
                    }); 
                    $(edit).updateHtml();
                    
                    $('#form-inserts #issue-lb, #form-inserts').removeClass('hidden');
                    $('#form-inserts').data('edit', true);
                    e.preventDefault();
                });
                
                /* Forms submit bindings */
                var milestoneform = formUtils.ajax("#milestone-lb form", function(data, form){
                    if ($(form).attr('rel')=='new'){
                        $("<li>").addClass('milestone').html(milestoneHtml(data.milestone))
                            .data(data.milestone).prependTo("#milestones");

                    } else {
                        $(edit).data(data.milestone);
                        $(edit).updateHtml();
                    }
                    load_milestones();
                    hide_forms();
                });

                var issueform = formUtils.ajax("#issue-lb form", function(data, form){
                    if(data.redirect_to) {
                        location.href = data.redirect_to;
                    } else {
                        if ($(form).attr('rel')=='new'){
                            $("<li/>").addClass('task').data(data.task)
                                .html(taskHtml(data.task)).prependTo("#tasks"); 

                        } else {
                            $(edit).data(data.task);
                            $(edit).updateHtml();
                        }
                    }
                    hide_forms();
                });
            };
            
            //init dashboard
            milestones_bindings();
            dragAndDrop();
            filters();   
            formsBindings();
        }
        
        Dashboard();
    }    
    
    
    $(".file").live("change", function(e){
        if(!$(this).attr('rel')){
            $(this).parent().append('<input type="file" class="file ">');
            $(this).attr('rel', 1);
        }
    })    
});

function subClass() {
  this.inheritFrom = superClass;
  this.inheritFrom();
  this.subtest = subTest; //attach method subTest
}

var formUtils = {
    showLoader:function(form){
        $(form).find(":submit").hide();
        $(form).find(".ajax-loader").addClass("init-loader");        
    },
    hideLoader:function(form){
        $(form).find(".ajax-loader").removeClass("init-loader");
        $(form).find(":submit").show();        
    },
    showErrors:function(validator, errors){
        for(var i=0; i<errors.length;i++){
            validator.showErrors(errors[i]);
        }
    },
    getJSON:function(form, validator){
        return {form: form, validator: validator, url : $(form).attr('action'), type : $(form).attr('method').toUpperCase(), data: $(form).serialize(), dataType: "json"}
    },
    ajax:function(selector, success){
        return $(selector).validate({
            submitHandler: function(form) {
                formUtils.showLoader(form);
                var json = formUtils.getJSON(form, this);
                json.success = function(data){
                    if(!data.valid){
                        formUtils.showErrors(this.validator, data.errors);
                    } else {
                        success(data, this.form);
                    }
                    formUtils.hideLoader(this.form);
                };
                $.ajax(json);
            }
        })        
    }
}
