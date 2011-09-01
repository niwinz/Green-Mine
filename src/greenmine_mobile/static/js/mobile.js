var dashboard_loadTasks = function(option_dom){
    var url = option_dom.attr('url');
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
            var option_dom = $(this).find('option:selected');
            dashboard_loadTasks(option_dom);
        });

        $(".issues-panel .issues-list .title a").live('click', function(e) {
            var options = $(this).parent().parent().find('.issue-options');
            if (options.hasClass('hidden')) options.removeClass('hidden');
            else options.addClass('hidden');
            e.preventDefault();
        });
        dashboard_loadTasks($(".milestones select option:selected"));
    }
})(jQuery);
