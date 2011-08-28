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
    
    if($("#dashboard").length){
        printTasks($("#milestones li.selected").attr("milestone"), $("#milestones li.selected").attr('milestoneurl'));
        
        $("#tasks-filters select").val(0);
        $("#tasks-filters").delegate("select", "change", function(){
            var selects = $("#tasks-filters select");
            var filters = new Array();
            for(var i=0; i<selects.length; i++){
                if($(selects[i]).val()!=''){
                    filters.push("["+$(selects[i]).attr('name')+"!="+$(selects[i]).val()+"]");
                }
            }
            
            if(filters.length>0){
                $("#tasks").hide();
                var tasks = $("#tasks li");
                $(tasks).show();
                $(tasks).filter(filters.join(',')).hide();
                $("#tasks").show();
            }else $("#tasks li").show();
        }); 
        
        $('#tasks').delegate('li', 'mouseenter', function() {
            var milestones = $("li.milestone");
            var milestones_length = milestones.length;
            for(var i=0; i<milestones_length; i++){
                if(!$(milestones[i]).is(':data(droppable)')) {
                    $(milestones[i]).droppable({activeClass: 'add',  tolerance: 'pointer', 
                    drop: function(ev, ui){
                        ui.draggable.draggable('option','revert',false);
                        if(!$(this).hasClass('selected')){
                            var data = {};
                            data.milestone = parseInt($(this).attr('milestone'));
                            data.task = parseInt($(ui.draggable).attr('task'));
                            $.ajax({url : '', type : 'POST', data: data});

                            var tasks = $(this).find('span.issue').html().split("/");
                            if($(ui.draggable).attr('state')=='fixed')tasks[0] = parseInt(tasks[0])+1;

                            tasks[1] = parseInt(tasks[1])+1;
                            $(this).find('span.issue').html(tasks[0]+"/"+tasks[1]);

                            var old_milestone_span = $("#milestones li[milestone='"+$("#tasks").attr('milestone')+"'] span.issue");
                            tasks = $(old_milestone_span).html().split("/");

                            if($(ui.draggable).attr('state')=='fixed')tasks[0] = parseInt(tasks[0])-1;

                            tasks[1] = parseInt(tasks[1])-1;
                            $(old_milestone_span).html(tasks[0]+"/"+tasks[1]); 

                            $(ui.draggable).remove();
                        }else{
                            ui.draggable.draggable('option','revert',true);
                        }
                    }
                    });
                }
            }
        });

        $("#milestones").delegate(".ml", "click", function(e){
            $("#milestones").find(".selected").removeClass("selected");
            var li = $(this).parent()
            $(li).addClass("selected");
            printTasks(parseInt($(li).attr("milestone")), $(li).attr("milestoneurl"))
        });

        $("#milestones").delegate(".edit", "click", function(e){
            e.preventDefault();
            var milestone = $(this).parent();
            var form = $("#milestone-lb form");
            $(form).attr('action', $(form).attr('editaction'));
            $("#milestone-lb input[name='estimated_finish']").val($(milestone).find('.estimated_finish').html());
            $("#milestone-lb input[name='name']").val($(milestone).find('.name').html()); 
            $("#milestone-lb input[name='id']").val($(milestone).attr('milestone')); 
            milestoneform.resetForm(); 
            openLightBoxMilestone();
        });
        
        $("#tasks").delegate(".edit", "click", function(e){
            e.preventDefault();
            var issue = $(this).parent();
            var form = $("#issue-lb form");
            $(form).attr('action', $(form).attr('editaction'));
            $("#issue-lb input[name='subject']").val($(issue).data('name'));
            $("#issue-lb select[name='type']").val($(issue).data('type')); 
            $("#issue-lb textarea[name='description']").val($(issue).data('description')); 
            $("#issue-lb input[name='id']").val($(issue).attr('id')); 
            issueform.resetForm(); 
            openLightBoxIssue();
        });  
        
        $("#new-milestone").click(function(e){
            e.preventDefault();
            var form = $("#milestone-lb form");
            $(form).each (function() {this.reset();});
            $(form).attr('action', $(form).attr('newaction'));
            milestoneform.resetForm(); 
            openLightBoxMilestone();
        });
        
        $("#new-issue").click(function(e){
            e.preventDefault();
            var form = $("#issue-lb form");
            $(form).each (function() {this.reset();});
            $(form).attr('action', $(form).attr('newaction'));
            issueform.resetForm(); 
            openLightBoxIssue();
        });        
        
        $("#close-issue-lb").click(function(e){
            e.preventDefault();
            closeLightBoxIssue();
        });        
        
        $("#close-milestone-lb").click(function(e){
            e.preventDefault();
            closeLightBoxMilestone();
        });
        
        var milestoneform = formUtils.ajax("#milestone-lb form", function(data){
            var html = '<li milestoneurl="'+data.milestoneurl+'" milestone="'+data.milestoneurl+'" class="milestone ui-droppable">' +
                        '<div class="ml"><span class="name">'+data.name+'</span><div><span class="estimated_finish">'+data.date+'</span> (<span class="issue">0/0</span>)</div></div>' +
                        '<a class="edit" href=""></a></li>';
            $("#milestones").prepend(html);                        
            $("#milestone-lb").fadeOut('fast');
        });
        
        var issueform = formUtils.ajax("#issue-lb form", function(data){
            if(data.redirect_to) location.href = data.redirect_to;
            else{
                printTask(data);
                $("#issue-lb").fadeOut('fast');
            }
        });        
    }
    
    if($("#issue").length){
        $("#issue").delegate(".delete-user", "click", function(e){
            $(this).parent().fadeOut("400", function(){  
                var realinput = $(this).parent().find("input[type='hidden']");
                var values = $(realinput).val().split(',');
                values.splice(jQuery.inArray($(this).attr('rel'),values),1);
                $(realinput).val(values.join(','));
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
                    $(realinput).val(values.join(','));
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
        
        $("#issue").delegate(".file", "change", function(e){
            if(!$(this).attr('rel')){
                $(this).parent().append('<input type="file" class="file ">');
                $(this).attr('rel', 1);
            }
        })
    }
    
    $( ".datepicker" ).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "dd/mm/yy"
    });
})

function openLightBoxIssue(){
    var left = ($(document).width()/2)-265; 
    var top = $(window).scrollTop()+100;
    $("#issue-lb").css({'top': top, 'left': left}).fadeIn('fast');  
}

function closeLightBoxIssue(){
    $("#issue-lb").fadeOut('fast');
}

function openLightBoxMilestone(){
    var left = ($(document).width()/2)-155; 
    var top = $(window).scrollTop()+100;
    $("#milestone-lb").css({'top': top, 'left': left}).fadeIn('fast');   
}

function closeLightBoxMilestone(){
    $("#milestone-lb").fadeOut('fast');
}

function printTask(data){
   $("<li/>").data(data).append('<div class="dg">'+
        data.name + '<span>[Asignado a: ' + data.to + ' | Estado: ' +
        data.state_view + ' | Prioridad: ' + data.priority_view + ' | Tipo: ' +
        data.type_view + ']</span></div><a class="edit" href=""></a>').appendTo('#tasks'); 
}

function printTasks(milestone, url){
    $("#tasks").attr('milestone', milestone);
    $.ajax({url : url, type : 'GET', dataType: "json",
        success: function(data){
            $("#tasks").html("");
            length_tasks = data.tasks.length;   
            for(var i=0; i<length_tasks; i++){
                 printTask(data.tasks[i]);
            }
            $("#tasks li").draggable({handle:'.dg', helper: 'clone', cursorAt: {cursor: "crosshair", top: -5, left: -5}, revert: 'invalid'});
        }
    });
}

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
                        success(data);
                    }
                    formUtils.hideLoader(this.form);
                };
                $.ajax(json);
            }
        })        
    }
}
