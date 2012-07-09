var dashboard_loadTasks = function(url){
    $.get(url, function(data) {
        var tasks_dom = $('.issues-panel');
        tasks_dom.hide();
        tasks_dom.html(data);
        tasks_dom.show();
    }, 'html');
};

(function($){
    if($('.project-panel').length){
        $(".milestones select").change(function() {
            var url = $(this).find('option:selected').attr('url');
            dashboard_loadTasks(url);
        });
        dashboard_loadTasks($(".milestones select option:selected").attr('url'));
    }
})(jQuery);
