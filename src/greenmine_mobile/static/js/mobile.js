var dashboard_loadTasks = function(option_dom){
    var url = option_dom.attr('url');
    var create_url = option_dom.attr('createurl');

    $('.new-us-button').attr('href', create_url);
    $.get(url, function(data) {
        var tasks_dom = $('.issues-module');
        tasks_dom.hide();
        tasks_dom.html(data);
        tasks_dom.show();
    }, 'html');
};

(function($){
    if($('.project-panel').length){
        $(".milestones select").change(function() {
            var option_dom = $(this).find('option:selected');
            dashboard_loadTasks(option_dom);
        });
        $('.us-item .us-title a').live('click', function(e) {
            var block = $(this).parent().parent().find('div.tasks');
            var self = $(this);

            if (block.hasClass('hidden')) { 
                block.hide();
                block.removeClass('hidden');
                block.slideDown('normal', function() {
                    self.parent().parent().addClass('selected');        
                });
            }
            else {
                block.slideUp('normal', function() {
                    block.addClass('hidden'); 
                    self.parent().parent().removeClass('selected');
                });
            }
            e.preventDefault();
        });
        dashboard_loadTasks($(".milestones select option:selected"));
    }
})(jQuery);
