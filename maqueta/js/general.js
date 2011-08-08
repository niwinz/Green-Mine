$(document).ready(function(){
    forms.init();
    
    if($("#login-form").length){
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
        $("#btn-usr-project").click(function(){
            var users = $("#edit-profile-form .valid[name='user-aux[]']:checked");
            if(users.length == 0){
                alert("Selecciona al menos un usuario");
            } else {
                var roles = $("#edit-profile-form [name='rol-aux']:checked");
                if(roles.length == 0){
                    alert("Selecciona un rol");
                } else {
                    var html = '';
                    for(var i=0; i<users.length; i++){
                        html += '<tr>';
                        html += '<td><img width="30" src="'+$(users[i]).attr('gravatar')+'">'+$(users[i]).attr('username')+'</td>';
                        html += '<td>'+$(roles[0]).attr('rolname')+'</td>';
                        html += '<td><a class="delete" rel="' + $(users[i]).val() + '" href="">Borrar</a></td>';
                        html += '<input type="hidden" name="user_'+$(users[i]).val()+'" value="'+$(roles[0]).val()+'" />';
                        html += '</tr>';
                        
                        $(users[i]).removeClass('valid');
                        $(users[i]).addClass('invalid');
                        $(users[i]).parent().hide();
                    }

                    $("#user-project tbody").append(html);
                    $("#user-project tbody").find("a.delete").click(function() {
                         var input = $("#edit-profile-form input[value='"+$(this).attr('rel')+"']");
                         $(input).removeClass('invalid');
                         $(input).addClass('valid');    
                         $(input).attr('checked', false);
                         $(input).parent().show();
                         $(this).parents('tr').remove();
                         return false;
                    });

                }
            }
            return false;
        });
    }
    
    if($("#dashboard").length){
        printMilestones(dashboard.milestones[0].id);
        printTasks(dashboard.milestones[0].tasks);
        
        $("#tasks").delegate(".dg", "mousedown", function(e){
            var li = $(this).parent();
            $(li).css("position", "absolute");
            $(li).attr('id', 'inmove');
            $(li).css({'top': e.pageY+10, 'left':e.pageX+20});
            e.preventDefault();

           $(document).mousemove(function(e){
              $('#inmove').css({'top': e.pageY+10, 'left':e.pageX+10});
            });        

            $(document).mouseup(function(e){
                var milestone = new Array();
                if($(e.target).hasClass("milestone"))milestone = $(e.target);
                else{
                   milestone = $(e.target).closest('li.milestone');
                }
                $(document).unbind('mousemove');
                $(document).unbind('mouseup');

                if(milestone.length && !$(milestone).hasClass('selected')){
                    //move the task    
                    var id_milestone = parseInt($(milestone).attr('milestone'));
                    var id_task = parseInt($('#inmove').attr('task'));
                    var length_milestones  = dashboard.milestones.length;
                    var length_tasks = 0;
                    var task = 0;

                    for(var i=0; i<length_milestones; i++){
                        length_tasks = dashboard.milestones[i].tasks.length;
                        for(var z=0; z<length_tasks; z++){
                            if(dashboard.milestones[i].tasks[z].id==id_task){
                                task = dashboard.milestones[i].tasks[z];
                                dashboard.milestones[i].tasks.splice(z,1); 
                                break;
                            }
                        }
                        if(task)break;
                    }
                    
                    if(!task){
                        length_tasks = dashboard.tasks.length;
                        for(z=0; z<length_tasks; z++){
                            if(dashboard.tasks[z].id==id_task){
                                task = dashboard.tasks[z];
                                dashboard.tasks.splice(z,1); 
                                break;
                            }
                        }                    
                    }

                    if(task){
                        if(id_milestone){
                            for(i=0; i<length_milestones; i++){
                                if(dashboard.milestones[i].id==id_milestone){
                                    dashboard.milestones[i].tasks.push(task);
                                    break;
                                }    
                            }
                        }else dashboard.tasks.push(task);
                        printMilestones($("#milestones").find('.selected').attr('milestone'));
                    }

                    $('#inmove').remove();
                }else{
                    $('#inmove').css("position", "relative");
                    $('#inmove').css({"top": 0, "left": 0}); 
                    $('#inmove').attr('id', '');                        
                }
            });   
        });        
        
        $("#milestones").delegate(".ml", "click", function(e){
            $("#milestones").find(".selected").removeClass("selected");
            var li = $(this).parent()
            $(li).addClass("selected");
            var id = parseInt($(li).attr("milestone"));

            if(id){
                var length_milestones  = dashboard.milestones.length;
                for(var i=0; i<length_milestones; i++){
                    if(dashboard.milestones[i].id == id){
                        printTasks(dashboard.milestones[i].tasks);
                        break;
                    }
                }
            }else printTasks(dashboard.tasks);
        });            
        
        $("#dashboard").delegate(".edit", "click", function(e){
            alert("popup");
            e.preventDefault();
        })        
        
    }
    
    if($(".messages-container li").length>0){
        setTimeout(function(){
            $(".messages-container").fadeOut('slow', function(){$(this).find("li").remove()});
        }, $(".messages-container li").length*4000);
    }
})

function printTasks(list){
    length_tasks = list.length;
    var html = '';        
    for(var i=0; i<length_tasks; i++){
        html+= '<li task="'+list[i].id+'" ><div class="dg">'+list[i].name+'<span>[Asignado a: '+list[i].assignedto+' | Estado: '+list[i].state+' | Prioridad: '+list[i].priority+' | Tipo: '+list[i].type+']</span></div><a class="edit" href=""><img width="21" src="imgs/cog.png" /></a></li>';
    }
    $("#tasks").html(html);
}

function printMilestones(sel){
    var length_milestones  = dashboard.milestones.length;
    var length_tasks = 0;
    var completedtasks = 0;
    var html = '';
    for(var i=0; i<length_milestones; i++){
        length_tasks = dashboard.milestones[i].tasks.length;
        completedtasks = 0;
        for(var z=0; z<length_tasks; z++){
            if(dashboard.milestones[i].tasks[z].state=='Cerrada'){
                completedtasks++;
            }
        }
        if(dashboard.milestones[i].id==sel)html+='<li milestone="'+dashboard.milestones[i].id+'" class="selected milestone">';
        else html+='<li milestone="'+dashboard.milestones[i].id+'" class="milestone">';
        html+='<div class="ml">'+dashboard.milestones[i].name+'<span>'+dashboard.milestones[i].enddate+' ('+completedtasks+'/'+length_tasks+')</span></div><a class="edit" href=""><img width="21" src="imgs/cog.png" /></a></li>';
    }
    
    if(sel==0)html+='<li milestone="0" class="selected milestone">';
    else html+='<li milestone="0" class="milestone">';    

    html+='<div class="ml">Sin asignar <span>('+dashboard.tasks.length+')</span></div></li>';
    $("#milestones").html(html);
}

var forms = {
    ajaxSuccess: '',
    init: function(){
        $(".validate").each(function(){
            $(this).validate({
                submitHandler: function() {
                    var ajaxsumit = $(this.currentForm).attr('ajaxsubmit');
                    if(ajaxsumit==undefined) ajaxsumit = 1;
                    else ajaxsumit = parseInt(ajaxsumit);
                    
                    if(ajaxsumit){    
                        forms.validate(this);
                    } else {
                       this.currentForm.submit();
                    }    
                }
            })
        })
    },
    validate:function(form){
        $(form.currentForm).find(":submit").hide();
        $(form.currentForm).find(".ajax-loader").addClass("init-loader");
        $.ajax({
            form: form,
            url : $(form.currentForm).attr('action'),
            type : $(form.currentForm).attr('method').toUpperCase(),
            data: $(form.currentForm).serialize(),
            dataType: "json",
            success: function(data){
                var form = this.form;
                if(!data.valid){
                    for(var i=0; i<data.errors.length;i++){
                        form.showErrors(data.errors[i]);
                    }
                } else {
                    if(data.redirect_to) location.href = data.redirect_to;
                    forms.ajaxSuccess();
                }

                $(form.currentForm).find(".ajax-loader").removeClass("init-loader");
                $(form.currentForm).find(":submit").show();
            }
        });
    }
}
