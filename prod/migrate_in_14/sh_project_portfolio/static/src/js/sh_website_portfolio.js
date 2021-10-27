

filterSelection("all") // Execute the function and show all columns
function filterSelection(c) {
  var x, i;
  x = document.getElementsByClassName("column");
  if (c == "all") c = "";
  // Add the "show" class (display:block) to the filtered elements, and remove the "show" class from the elements that are not selected
  for (i = 0; i < x.length; i++) {
    shRemoveClass(x[i], "show");
    if (x[i].className.indexOf(c) > -1) shAddClass(x[i], "show");
  }
}

// Show filtered elements
function shAddClass(element, name) {
  var i, arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (i = 0; i < arr2.length; i++) {
    if (arr1.indexOf(arr2[i]) == -1) {
      element.className += " " + arr2[i];
    }
  }
}

// Hide elements that are not selected
function shRemoveClass(element, name) {
  var i, arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (i = 0; i < arr2.length; i++) {
    while (arr1.indexOf(arr2[i]) > -1) {
      arr1.splice(arr1.indexOf(arr2[i]), 1);
    }
  }
  element.className = arr1.join(" ");
}

// Add active class to the current button (highlight it)
var btnContainer = document.getElementById("myBtnContainer");

var btnContainer = $('#myBtnContainer');
var btns=$('.btn');
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function(){
	var current = $('.active');
    current[0].className = current[0].className.replace(" active", "");
    this.className += " active";
  });
}


// show all automatic active when page load
$(document).ready(function(){
jQuery(function(){
	   jQuery('#sh_show_all_project_btn').click();
	   $('#sh_show_all_project_btn').addClass("active");
	});
});

//set active class on button
$(document).ready(function(){
    $("button").click(function(){
    	$("button").removeClass("active").addClass("btn");
    	$(this).addClass("active");
    });
    var $container = $('#posts').isotope({
        itemSelector: '.item',
        isFitWidth: true
    });

    $(window).smartresize(function() {
        $container.isotope({
            columnWidth: '.col-sm-6'
        });
    });

    $container.isotope({
        filter: '*'
    });

    // filter items on button click
    $('#filters').on('click', 'button', function() {
        var filterValue = $(this).attr('data-filter');
        $container.isotope({
            filter: filterValue
        });
    });

    //active filter check
    $(".button_bg").click(function() {
        $(".button_bg").removeClass("active_port");
        $(this).addClass("active_port");
    });
});



//new full width slider js


/*$('#carouselExampleIndicators').carousel();
var winWidth = $(window).innerWidth();
$(window).resize(function () {

    if ($(window).innerWidth() < winWidth) {
        $('.carousel-inner>.item>img').css({
            'min-width': winWidth, 'width': winWidth
        });
    }
    else {
        winWidth = $(window).innerWidth();
        $('.carousel-inner>.item>img').css({
            'min-width': '', 'width': ''
        });
    }
});
*/






