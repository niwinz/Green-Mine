$(document).ready(function(){
	forms.init();
	
	if($("#login-form").length){
		$("#open-forgotten-password-form").click(function(e){
			$("#login-form").fadeOut("fast", function() {
				$("#forgotten-password-form").fadeIn("fast");
  			});
			e.preventDefault();
		})	
	
		$("#close-forgotten-password-form").click(function(e){
			$("#forgotten-password-form").fadeOut("fast", function() {
				$("#login-form").fadeIn("fast");
  			});
			e.preventDefault();
		})
	}//#login-form

	if($("#project").length){
		$("#btn-usr-project").click(function(){
			var users = $("#edit-profile-form .valid[name='user-aux[]']:checked");
                        if(users.length==0){
                            alert("Selecciona al menos un usuario");
                        }else{
                            var roles = $("#edit-profile-form [name='rol-aux']:checked");
                            if(roles.length==0){
                                alert("Selecciona un rol");
                            }else{
                                var html = '';
                                for(var i=0; i<users.length; i++){
                                    html += '<tr>';
                                    html += '<td><img width="30" src="'+$(users[i]).attr('gravatar')+'">'+$(users[i]).attr('username')+'</td>';
                                    html += '<td>'+$(roles[0]).attr('rolname')+'</td>';
                                    html += '<td><a class="delete" href="" onclick="return deleteUserRolProject(this, \''+$(users[i]).val()+'\')">Borrar</a></td>';
                                    html += '<input type="hidden" name="users[]['+$(users[i]).val()+']" value="'+$(roles[0]).val()+'" />';
                                    html += '</tr>';
                                    
                                    $(users[i]).removeClass('valid');
                                    $(users[i]).addClass('invalid');
                                    $(users[i]).parent().hide();
                                }
                                $("#user-project tbody").append(html);
                            }
                        }
		});
	}//#project

        if($("#dashboard").length){
            $("#dashboard .edit").click(function(){
                alert("popup")
            })
        }
});

function deleteUserRolProject(elm, id){
    var input = $("#edit-profile-form [value='"+id+"']");
    $(input).removeClass('invalid');
    $(input).addClass('valid');    
    $(input).attr('checked', false);
    $(input).parent().show();
    $(elm).parent().parent().remove();
    return false;
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
                        }else{
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
                        type : "GET",
                        data: $(form.currentForm).serialize(),
                        dataType: "json",
                        success: function(data){
                                var form = this.form;
                                if(!data.valid){
                                        for(var i=0; i<data.errors.length;i++){
                                                form.showErrors(data.errors[i]);
                                        }
                                }else{
                                        forms.ajaxSuccess();
                                }

                                $(form.currentForm).find(".ajax-loader").removeClass("init-loader");
                                $(form.currentForm).find(":submit").show();
                        }
                })
	}
}
