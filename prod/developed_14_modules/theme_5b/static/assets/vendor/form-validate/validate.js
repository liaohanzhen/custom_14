/**
* PHP Email Form Validation - v2.0
* URL: https://bootstrapmade.com/php-email-form/
* Author: BootstrapMade.com
*/

$('document').ready(function() {
  $('form.contact_us_form').submit(function(e) {
    var f = $(this).find('.form-group'),
      ferror = false,
      emailExp = /^[^\s()<>@,;:\/]+@\w[\w\.-]+\.[a-z]{2,}$/i;

    f.children('input').each(function() { // run all inputs
     
      var i = $(this); // current input
      var rule = i.attr('data-rule');

      if (rule !== undefined) {
        var ierror = false; // error flag for current input
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }
        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;

          case 'email':
            if (!emailExp.test(i.val())) {
              ferror = ierror = true;
            }
            break;

          case 'checked':
            if (! i.is(':checked')) {
              ferror = ierror = true;
            }
            break;

          case 'regexp':
            exp = new RegExp(exp);
            if (!exp.test(i.val())) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validate').html((ierror ? (i.attr('data-msg') !== undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });

    f.children('textarea').each(function() { // run all inputs
      var i = $(this); // current input
      var rule = i.attr('data-rule');
      if (rule !== undefined) {
        var ierror = false; // error flag for current input
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validate').html((ierror ? (i.attr('data-msg') != undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });

    f.children('select').each(function() { // run all inputs
      var i = $(this); // current input
      var rule = i.attr('data-rule');
      if (rule !== undefined) {
        var ierror = false; // error flag for current input
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validate').html((ierror ? (i.attr('data-msg') != undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });

    if (ferror){e.preventDefault(); return false; }
    else { 
		$(this).find('button').prop('disabled', true); 
		$(this).find('img').show(); 
		//alert($(this).find('input[name="form_type"]').val())
		
		if ($(this).find('input[name="form_type"]').val() == 'general'){
			e.preventDefault();
			contactFormAjax();
		}
		else if ($(this).find('input[name="form_type"]').val() == 'outside'){
			e.preventDefault();
			contactFormAjaxOutside();
		}
		else if ($(this).find('input[name="form_type"]').val() == 'become'){
			e.preventDefault();
			contactFormAjaxBecome();
		}
		else
			return true
	}
  });
  
  $("#o_know_how").change(function() {
	if(this.value === 'Other')
		$(".o_show_other").show();
	else
		$(".o_show_other").hide();
  });
  $("#know_how").change(function() {
	if(this.value === 'Other')
		$(".show_other").show();
	else
		$(".show_other").hide();
  });
  $("#b_know_how").change(function() {
	if(this.value === 'Other')
		$(".b_show_other").show();
	else
		$(".b_show_other").hide();
  });
  
});
