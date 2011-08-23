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

    if($("#project").length){
        var autocomplete_selector = "input.user-autocomplete";

        var getRemoteData = function(request, response) {
            var url = $(autocomplete_selector).attr('url');
            url = url + "?term=" + request.term;
            $.get(url,  function(data) {
                if (data.valid){
                    response(data.list);
                }
            }, 'json');
        };
        var selectItem = function(event, ui) {
            var currentuser_dom = $(autocomplete_selector).parent().find("input.user-currentvalue");
            currentuser_dom.val(ui.item.id);
            currentuser_dom.attr('name', ui.item.value);
            currentuser_dom.attr('gravatar', ui.item.gravatar);

            console.log(ui.item);
        };

        $(autocomplete_selector).autocomplete({
            source: getRemoteData,
            minLength: 1,
            select: selectItem
        });

        $("#btn-usr-project").click(function(e){
            var roles = $("#edit-profile-form [name='rol-aux']:checked");
            if (roles.length == 0){
                alert("Selecciona un rol");
            } else {
                var user = $(autocomplete_selector).parent().find("input.user-currentvalue");
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
                        $(autocomplete_selector).val("");
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

                            var tasks = $(this).find('span').html().split("/");
                            if($(ui.draggable).attr('state')=='fixed')tasks[0] = parseInt(tasks[0])+1;

                            tasks[1] = parseInt(tasks[1])+1;
                            $(this).find('span').html(tasks[0]+"/"+tasks[1]);

                            var old_milestone_span = $("#milestones li[milestone='"+$("#tasks").attr('milestone')+"'] span");
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

        $("#dashboard").delegate(".edit", "click", function(e){
            alert("popup");
            e.preventDefault();
        })
        
        $("#new-milestone").click(function(e){
            e.preventDefault();
            var left = ($(document).width()/2)-155; 
            var top = $(window).scrollTop()+100;
            $("#milestone-lb").css({'top': top, 'left': left});
            $("#milestone-lb").fadeIn('fast');
        });
        
        $("#close-milestone-lb").click(function(e){
            e.preventDefault();
            $("#milestone-lb").fadeOut('fast');
        });
        
        formUtils.ajax("#milestone-lb form", function(data){
            var html = '<li milestoneurl="'+data.milestoneurl+'" milestone="'+data.milestoneurl+'" class="milestone ui-droppable">' +
                        '<div class="ml">'+data.name+'<div>'+data.date+' (<span>0/0</span>)</div></div>' +
                        '<a class="edit" href=""><img width="21" src="imgs/cog.png"></a></li>';
            $("#milestones").append(html);                        
            $("#milestone-lb").fadeOut('fast');
        });
    }
    
    $( ".datepicker" ).datepicker({
        changeMonth: true,
        changeYear: true
    });         
    
    if($(".messages-container li").length>0){
        setTimeout(function(){
            $(".messages-container").fadeOut('slow', function(){$(this).find("li").remove()});
        }, $(".messages-container li").length*4000);
    }
})

function printTasks(milestone, url){
    $("#tasks").attr('milestone', milestone);
    $.ajax({url : url, type : 'GET', dataType: "json",
        success: function(data){
            length_tasks = data.tasks.length;
            var html = '';        
            for(var i=0; i<length_tasks; i++){
                html += '<li state="' + data.tasks[i].state + '"  to="' + data.tasks[i].to_id + '" priority="'+
                    data.tasks[i].priority + '" type="' + data.tasks[i].type + '" task="'+data.tasks[i].id + '" ><div class="dg">'+
                    data.tasks[i].name + '<span>[Asignado a: ' + data.tasks[i].to + ' | Estado: ' +
                    data.tasks[i].state_view + ' | Prioridad: ' + data.tasks[i].priority_view + ' | Tipo: ' +
                    data.tasks[i].type_view + ']</span></div><a class="edit" href=""><img width="21" src="/static/imgs/cog.png" /></a></li>';
            }
            $("#tasks").html(html);
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
        $(selector).validate({
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