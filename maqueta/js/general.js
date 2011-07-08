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
});

var forms = {
	init: function(){
		$(".validate").each(function(){
			$(this).validate({
			 submitHandler: function() {
				forms.validate(this);
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
					//¿reload?
				}

				$(form.currentForm).find(".ajax-loader").removeClass("init-loader");
				$(form.currentForm).find(":submit").show();
			}
		})
	}
}
