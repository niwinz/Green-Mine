(function($){
    $(".btn01, input[type='submit'], input[type='button']").button();
    $( ".datepicker, #id_finish_date" ).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "dd/mm/yy"
    });
})(jQuery);

$(document).ready(function(){
    $(".validate").validate();
    
    if($("#login-form").length){
        formUtils.ajax("#login-form, #forgotten-password-form", function(data){
            if(data.redirect_to) location.href = data.redirect_to;
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
                var url = $("input.user-autocomplete").attr('url');
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
    
    if($("#dashboard").length){        
        function Dashboard(){  
            $.fn.updateHtml = function(){
                if($(this).hasClass('milestone')){
                    $(this).html(milestoneHtml($(this).data()));
                }else{
                    if($(this).hasClass('task')){
                        $(this).html(taskHtml($(this).data()));
                    }
                }
            };                
            
            function milestoneHtml(ml){
                var html =  '<div class="ml"><span class="name">'+ml.name+'</span><div>';
                if(ml.id){
                     html+= '<span class="estimated_finish">'+ml.estimated_finish+'</span>';
                }
                    
                html+=' (<span class="issue">'+ml.completed_tasks+'/'+ml.total_tasks+'</span>)</div></div>';

                if(ml.id){
                    html+='<a href="" class="edit"></a>';
                }
                return html;
            }
            
            function taskHtml(tk){
                var html = '<div class="dg">%s<span>[ Estado: %s | Prioridad: %s ]</span></div>'
                    + '<a class="edit" href=""></a><a href="%s" class="detail"></a>';
                return interpolate(html, [tk.subject,tk.status_view,tk.priority_view,tk.url]);
            }            
            
            function loadTasks(url){
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
            
            function dragAndDrop(){
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
            
            var filters = function(){
                $("#tasks-filters select").val(-1);
                $("#tasks-filters").delegate("select", "change", function(){
                    var selects = $("#tasks-filters select");
                    var lis = $("#tasks li");
                    $(lis).hide();
                    $(lis).filter(function() {
                        var show = true;
                        var ln = selects.length;

                        for(var i=0; i<ln; i++){
                            if($(selects[i]).val()!=-1){
                                if($(this).data($(selects[i]).attr("name"))!=$(selects[i]).val()){
                                    show = false;
                                    break;
                                }
                            }
                        }
                        return show
                    }).show();
                });            
            };

            var formsBindings = function() {
                var edit = null;

                $("#new-milestone").click(function(e) {
                    e.preventDefault();
                });
                $("#new-issue").click(function(e) {
                    $('#form-inserts #issue-lb, #form-inserts').removeClass('hidden');
                    var form = $("#form-inserts #issue-lb form");
                    $(form).each (function() {this.reset();});
                    $(form).attr('action', $(form).attr('newaction'));
                    $(form).attr('rel', 'new');
                    e.preventDefault();
                });
                $('#new-milestone').click(function(e) {
                    $('#form-inserts #milestone-lb, #form-inserts').removeClass('hidden');
                    var form = $("#form-inserts #milestone-lb form");

                    $(form).each (function() {this.reset();});
                    $(form).attr('action', $(form).attr('newaction'));
                    $(form).attr('rel', 'new');
                    e.preventDefault();
                });
                $('#form-inserts #milestone-lb .cancel').click(function(e) {
                    $('#form-inserts #milestone-lb, #form-inserts').addClass('hidden');
                    e.preventDefault();
                });
                $('#form-inserts #issue-lb .cancel').click(function(e) {
                    $('#form-inserts #issue-lb, #form-inserts').addClass('hidden');
                    e.preventDefault();
                });

                $("#milestones").delegate(".edit", "click", function(e){
                    edit = $(this).parent();
                    var form = $("#milestone-lb form");
                    
                    $(form).each (function() {this.reset();});
                    $(form).attr('action', $(edit).data('edit_url'));
                    $(form).attr('rel', 'edit');
                    milestoneform.reset();

                    $.each($(edit).data(), function(key, value) { 
                       $(form).find("[name='"+key+"']").val(value);
                    });

                    $('#form-inserts #milestone-lb, #form-inserts').removeClass('hidden');
                    e.preventDefault();
                });
                
                /* 
                 * TODO: en este caso pensar si mejor hacer un inline con un formulario
                 * cargado directo por ajax. ya que en una lista larga al clickar, el formulario
                 * se desplegara en la parte superior, y no seria comodo a la hora de editar.
                */
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
                    
                    $('#form-inserts #issue-lb, #form-inserts').removeClass('hidden');
                    e.preventDefault();
                });

                var milestoneform = formUtils.ajax("#milestone-lb form", function(data, form){
                    if ($(form).attr('rel')=='new'){
                        $("<li>").addClass('milestone').html(milestoneHtml(data.milestone))
                            .data(data.milestone).prependTo("#milestones");

                    } else {
                        $(edit).data(data.milestone);
                        $(edit).updateHtml();
                    }
                    load_milestones();
                    $('#form-inserts #milestone-lb, #form-inserts').addClass('hidden');
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
                    $('#form-inserts #issue-lb, #form-inserts').addClass('hidden');
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
