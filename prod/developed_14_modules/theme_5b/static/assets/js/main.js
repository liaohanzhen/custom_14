/**
* Template Name: Mentor - v2.1.0
* Template URL: https://bootstrapmade.com/mentor-free-education-bootstrap-theme/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
$('document').ready(function() {
	
  // Preloader
	if ($('#preloader').length) {
	  $('#preloader').delay(100).fadeOut('slow', function() {
		$(this).remove();
	  });
	}

	// Smooth scroll for the navigation menu and links with .scrollto classes
	var scrolltoOffset = $('#header').outerHeight() - 1;
  
	$(document).on('click', '.nav-menu a, .mobile-nav a, .scrollto', function(e) {
	  //console.log("Menu clicked")
	if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
	  var target = $(this.hash);
	  if (target.length) {
		e.preventDefault();

		var scrollto = target.offset().top - scrolltoOffset;

		if ($(this).attr("href") == '#header') {
		  scrollto = 0;
		}

		$('html, body').animate({
		  scrollTop: scrollto
		}, 1500, 'easeInOutExpo');

		if ($(this).parents('.nav-menu, .mobile-nav').length) {
		  $('.nav-menu .active, .mobile-nav .active').removeClass('active');
		  $(this).closest('li').addClass('active');
		}

		if ($('body').hasClass('mobile-nav-active')) {
		  $('body').removeClass('mobile-nav-active');
		  $('.mobile-nav-toggle i').toggleClass('fa-bars fa-times');
		  $('.mobile-nav-overly').fadeOut();
		}
		return false;
	  }
	}
	});

  // Activate smooth scroll on page load with hash links in the url
	if (window.location.hash) {
	  var initial_nav = window.location.hash;
	  if ($(initial_nav).length) {
		var scrollto = $(initial_nav).offset().top - scrolltoOffset;
		$('html, body').animate({
		  scrollTop: scrollto
		}, 1500, 'easeInOutExpo');
	  }
	}

  // Mobile Navigation
  if ($('.nav-menu').length) {
	  console.log("Menu toggled")
    var $mobile_nav = $('.nav-menu').clone().prop({
      class: 'mobile-nav d-lg-none'
    });
    $('body').append($mobile_nav);
    $('body').prepend('<button type="button" class="mobile-nav-toggle d-lg-none"><i class="fa fa-bars"></i></button>');
    $('body').append('<div class="mobile-nav-overly"></div>');

    $(document).on('click', '.mobile-nav-toggle', function(e) {
      $('body').toggleClass('mobile-nav-active');
      $('.mobile-nav-toggle i').toggleClass('fa-bars fa-times');
      $('.mobile-nav-overly').toggle();
    });

    $(document).on('click', '.mobile-nav .drop-down > a', function(e) {
      e.preventDefault();
      $(this).next().slideToggle(300);
      $(this).parent().toggleClass('active');
    });

    $(document).click(function(e) {
      var container = $(".mobile-nav, .mobile-nav-toggle");
      if (!container.is(e.target) && container.has(e.target).length === 0) {
        if ($('body').hasClass('mobile-nav-active')) {
          $('body').removeClass('mobile-nav-active');
          $('.mobile-nav-toggle i').toggleClass('fa-bars fa-times');
          $('.mobile-nav-overly').fadeOut();
        }
      }
    });
  } else if ($(".mobile-nav, .mobile-nav-toggle").length) {
    $(".mobile-nav, .mobile-nav-toggle").hide();
  }

  // Back to top button
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $('.back-to-top').fadeIn('slow');
    } else {
      $('.back-to-top').fadeOut('slow');
    }
  });

  $('.back-to-top').click(function() {
    $('html, body').animate({
      scrollTop: 0
    }, 1500, 'easeInOutExpo');
    return false;
  });
  
  var url = $(location).attr('href');
  if(url.substr(-1) == '/'){
	$('nav').removeClass("navbar-light");
	$('nav').removeClass("bg-light");
	$('header').addClass("header_color");
	
	//$('#top_menu_collapse').addClass("justify-content-end");
	//$('#top_menu').removeClass("flex-grow-1");
	
	$(".slider_image").removeAttr( "loading" )
	$('.logo > span > img').attr('src','/theme_5b/static/img/5B_LOGO_White.png');
	var navbar_height =  $('header').outerHeight();
	$(window).scroll(function(){  
		if ($(this).scrollTop() > 201) {
			$('header').css('height', navbar_height + 'px');
			$('header').removeClass("header_color");
			$('.logo > span > img').attr('src','/theme_5b/static/img/5B_LOGO_Color.png');
		}
		else{
			$('nav').removeClass("navbar-light");
			$('nav').removeClass("bg-light");
			$('header').addClass("header_color");
			$('header').css('height', 'auto');
			$('.logo > span > img').attr('src','/theme_5b/static/img/5B_LOGO_White.png');
		}   
	});
  }
  else{
	$('nav').removeClass("navbar-light");
	$('header').removeClass("header_color");
	$('header').addClass("background_white");
	$(".slider_image").removeAttr( "loading" );
	//$('#top_menu_collapse').addClass("justify-content-end");
	//$('#top_menu').removeClass("flex-grow-1");
	$('.logo > span > img').attr('src','/theme_5b/static/img/5B_LOGO_Color.png');
  }
  
	$(".moreBox").slice(0, 6).show();
	//console.log($(".moreBox:hidden").length)
	if ($(".moreBox:hidden").length !== 0) {
		$("span.remaining_project").html($(".moreBox:hidden").length);
		$("#loadMore").show();
	}  else {
		$("#loadMore").hide();
	}				
	$("#loadMore").on('click', function (e) {
	  e.preventDefault();
	  $(".moreBox:hidden").slice(0, 6).slideDown();
	  $("span.remaining_project").html($(".moreBox:hidden").length);
	  if ($(".moreBox:hidden").length == 0) {
		$("#loadMore").fadeOut('slow');
	  }
	});
	
	$(".moreBoxVideo").slice(0, 3).show();
	if ($(".moreBoxVideo:hidden").length !== 0) {
		$("span.remaining_videos").html($(".moreBoxVideo:hidden").length);
		$("#loadMoreVideo").show();
	}  else {
		$("#loadMoreVideo").hide();
	}
	$("#loadMoreVideo").on('click', function (e) {
	  e.preventDefault();
	  $(".moreBoxVideo:hidden").slice(0, 3).slideDown();
	  $("span.remaining_videos").html($(".moreBoxVideo:hidden").length);
	  if ($(".moreBoxVideo:hidden").length == 0) {
		$("#loadMoreVideo").fadeOut('slow');
	  }
	});
	
	$(".moreBoxNews").slice(0, 3).show();
	if ($(".moreBoxNews:hidden").length !== 0) {
		$("span.remaining_news").html($(".moreBoxNews:hidden").length);
		$("#loadMoreNews").show();
	}  else {
		$("#loadMoreNews").hide();
	}				
	$("#loadMoreNews").on('click', function (e) {
	  e.preventDefault();
	  $(".moreBoxNews:hidden").slice(0, 3).slideDown();
	  $("span.remaining_news").html($(".moreBoxNews:hidden").length);
	  if ($(".moreBoxNews:hidden").length == 0) {
		$("#loadMoreNews").fadeOut('slow');
	  }
	});
	
	$('#uploadFormSubscriptionSubmit').click(function() {
		$('#uploadFormSubscription').submit();
	  });
	
});

(function() {

  'use strict';

  /**
   * tabs
   *
   * @description The Tabs component.
   * @param {Object} options The options hash
   */
  var tabs = function(options) { 

    var el = document.querySelector(options.el);
    var tabNavigationLinks = el.querySelectorAll(options.tabNavigationLinks);
    var tabContentContainers = el.querySelectorAll(options.tabContentContainers);
    var initCalled = false;
	var _location = window.location.href
	if(_location.includes('get_a_quote')){
		var activeIndex = 2;
		tabNavigationLinks[0].classList.remove('is-active');
        tabNavigationLinks[activeIndex].classList.add('is-active');
		tabContentContainers[0].classList.remove('is-active');
        tabContentContainers[activeIndex].classList.add('is-active');
	}
	else
		var activeIndex = 0;
    /**
     * init
     *
     * @description Initializes the component by removing the no-js class from
     *   the component, and attaching event listeners to each of the nav items.
     *   Returns nothing.
     */
    var init = function() {
      if (!initCalled) {
        initCalled = true;
        el.classList.remove('no-js');
        for (var i = 0; i < tabNavigationLinks.length; i++) {
          var link = tabNavigationLinks[i];
          handleClick(link, i);
        }
      }
    };

    /**
     * handleClick
     *
     * @description Handles click event listeners on each of the links in the
     *   tab navigation. Returns nothing.
     * @param {HTMLElement} link The link to listen for events on
     * @param {Number} index The index of that link
     */
    var handleClick = function(link, index) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        goToTab(index);
      });
    };

    /**
     * goToTab
     *
     * @description Goes to a specific tab based on index. Returns nothing.
     * @param {Number} index The index of the tab to go to
     */
    var goToTab = function(index) {
      if (index !== activeIndex && index >= 0 && index <= tabNavigationLinks.length) {
        tabNavigationLinks[activeIndex].classList.remove('is-active');
        tabNavigationLinks[index].classList.add('is-active');
        tabContentContainers[activeIndex].classList.remove('is-active');
        tabContentContainers[index].classList.add('is-active');
        activeIndex = index;
      }
    };

    /**
     * Returns init and goToTab
     */
    return {
      init: init,
      goToTab: goToTab
    };

  };

  /**
   * Attach to global namespace
   */
  window.tabs = tabs;

})();
