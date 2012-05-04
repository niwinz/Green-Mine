(function($){
 $.fn.lightbox = function(self) {
     var defaults = {
        opacity: 0.8,
        background: '#000000',
        lightboxTop: 50,
        overrideTop: false,
        overrideLeft: false,
        valing: true,
        overlay: $("#overlay"), /* false to disabled */
        forceReload: true,
        fadeIn: false,
        fadeInDuration: 'slow',
        fadeOut: false,
        fadeOutDuration: 'slow',        
        source: 'none', /* none, ajax, iframe */
        iframeSource: false,
        iframeWidth: '',
        iframeHeight: '',
        iframeSourceTarget: false,
        ajaxSource: false,
        ajaxSourceTarget: false,
        ajaxInit: function(){},
        ajaxEnd: function(){},
        onload: function(){},
        openstandard: function(){
            if(this.overlay){                 
                this.overlay.css({
                    'height': $(document).height(),
                    'width': $(window).width(),
                    'background': this.background,
                    'opacity': this.opacity
                });
                var self = this;
                this.overlay.click(function(){
                    self.close();
                    $(this).unbind('click');
                });
            }
                    
            $('.klightbox').css('z-index', 95);
            
            if(!this.first_load || this.forceReload){
                if(this.source=='iframe' && this.iframeSource){
                    var iframe = $(document.createElement('iframe'))
                    .attr({'src': this.iframeSource, 'width': this.iframeWidth, 'height': this.iframeHeight});
                    
                    if(this.iframeSourceTarget){
                        this.iframeSourceTarget.html(iframe);
                    }else{
                        this.selector.html(iframe);
                    }
                }

                this.selector.css({
                    'display': 'block',
                    'position': 'absolute',
                    'width': self.width,
                    'visibility': 'hidden'
                });
                                
                if(this.overrideTop){
                    top = this.overrideTop;
                }else{
                    if(this.valing){
                        var top = ($(document).scrollTop()) + ($(window).height()/2) - (this.selector.outerHeight()/2);
                        if (top < this.lightboxTop) {
                            top = $(document).scrollTop()+this.lightboxTop;
                        }                      
                    }else{
                        top = $(document).scrollTop()+this.lightboxTop;
                    }
                }    
                
                if(this.overrideLeft){
                    left = this.overrideLeft;
                }else{
                    left = ($(document).width()/2)-(this.width/2);
                }
                
                this.selector.css({
                    'display': 'none',
                    'visibility': 'visible',
                    'left': left,
                    'top': top,
                    'z-index': 100
                });
                
                this.first_load = true;
            }
            
            if(this.fadeIn){
                if(this.overlay) this.overlay.fadeIn(this.fadeInDuration);
                this.selector.fadeIn(this.fadeInDuration, this.onload);
            }else{
                if(this.overlay) this.overlay.show();
                this.selector.show();
                this.onload();
            } 
        },
        open: function(){
            if(this.source=='ajax' && this.ajaxSource && (!this.first_load || this.forceReload)){
                $("#ajax-loader").css({
                    'top': ($(document).scrollTop()) + ($(window).height()/2) - (55/2),
                    'left': ($(document).width()/2)-(54/2),
                    'display': 'block'
                });                
                this.ajaxInit();
                var self = this;
                $.ajax({
                  url: this.ajaxSource,
                  success: function(data){
                    if(self.ajaxSourceTarget){
                        self.ajaxSourceTarget.html(data);
                    }else{
                        self.selector.html(data);
                    }
                    self.ajaxEnd();
                    self.openstandard();
                  }
                });
            }else{
                this.openstandard();
            }
        },
        close: function(){
            $("#ajax-loader").hide();
            if(this.fadeOut){
                if(this.overlay) this.overlay.fadeOut(this.fadeOutDuration);
                this.selector.fadeOut(this.fadeOutDuration);
            }else{
                if(this.overlay) this.overlay.hide();
                this.selector.hide();
            }
            this.selector.data('status', 'closed');
        }
     };
     
     if($(this).data('lightbox')!=undefined){
        var self = $.extend($(this).data('lightbox'), self); 
     }else{
        var self = $.extend(defaults, self);    
        self.first_load = false;
        self.selector = $(this);        
     }
     
     $(this).data('lightbox', self);
     return self;
 };  
})(jQuery);
