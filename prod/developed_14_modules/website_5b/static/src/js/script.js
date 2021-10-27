function contactFormAjax(){
	odoo.define('web.ajax2', function(require){
	'use strict'; 
	var ajax = require('web.ajax');
	
		var name = $('input[name="name"]').val()
		var email = $('input[name="email"]').val()
		var phone = $('input[name="phone"]').val()
		var company = $('input[name="company"]').val()
		var c_type = $('select[name="type"]').val()
		var subject = $('input[name="subject"]').val()
		var know_how = $('select[name="know_how"]').val()
		var check = $('#check').is(':checked')
		if (check)
			check = 'Yes'
		else
			check = 'No'
		
		var other_source = '';
		if(know_how === 'Other')
			other_source = $('input[name="other_source"]').val()
		
		var message = $('textarea[name="message"]').val()
		
		
		var res = ajax.jsonRpc("/submit/contact", 'call', {
			'name' : name,
			'email': email,
			'phone': phone,
			'company' : company,
			'type' : c_type,
			'subject': subject,
			'know_how': know_how,
			'other_source':other_source,
			'check':check,
			'message': message
		}).then(function(returnval){
			returnval = JSON.parse(returnval);
			if(returnval['status'] == 'OK'){
				//alert("Success general")
				$(location).attr('href',returnval['return_link']+"success");
			} else {
				//alert("Failed general")
				$(location).attr('href',returnval['return_link']+"failed");
			}
		});
		
	})
}

function careerFormAjax(){
	odoo.define('web.ajax2', function(require){
	'use strict'; 
	var ajax = require('web.ajax');
	
		var firstname = $('input[name="firstname"]').val()
		var lastname = $('input[name="lastname"]').val()
		var email = $('input[name="email"]').val()
		var phone = $('input[name="phone"]').val()
		var relevant_team = $('select[name="relevant_team"]').val()
		var message = $('textarea[name="message"]').val()
		var check = $('#check').is(':checked')
		if (check)
			check = 'Yes'
		else
			check = 'No'
		
		full_name = firstname + " " + lastname
		
		var res = ajax.jsonRpc("/submit/careers", 'call', {
			'firstname' : firstname,
			'lastname' : lastname,
			'email': email,
			'phone': phone,
			'team' : relevant_team,
			'message': message,
			'check': check
		}).then(function(returnval){
			returnval = JSON.parse(returnval);
			if(returnval['status'] == 'OK'){
				//alert("Success career")
				$(location).attr('href',returnval['return_link']+"success");
			} else {
				//alert("Failed career")
				$(location).attr('href',returnval['return_link']+"failed");
			}
		});
	})
}

function contactFormAjaxOutside(){
	odoo.define('web.ajax2', function(require){
	'use strict'; 
	var ajax = require('web.ajax');
	
		var name = $('input[name="o_name"]').val()
		var email = $('input[name="o_email"]').val()
		var phone = $('input[name="o_phone"]').val()
		var company = $('input[name="o_company"]').val()
		var company_role = $('input[name="o_company_role"]').val()
		var website = $('input[name="o_website"]').val()
		
		var company_type = $('select[name="o_company_type"]').val()
		var country = $('select[name="o_country"]').val()
		
		var project_name = $('input[name="o_project_name"]').val()
		var project_pipeline = $('input[name="o_project_pipeline"]').val()
		
		var know_how = $('select[name="o_know_how"]').val()
		var check = $('#o_check').is(':checked')
		if (check)
			check = 'Yes'
		else
			check = 'No'
		
		var other_source = '';
		
		if(know_how === 'Other')
			other_source = $('input[name="o_other_source"]').val()
		
		var message = $('textarea[name="o_message"]').val()
		
		var res = ajax.jsonRpc("/submit/outside", 'call', {
			'name' : name,
			'email': email,
			'phone': phone,
			'company' : company,
			'company_role' : company_role,
			'website' : website,
			'company_type' : company_type,
			'country' : country,
			'project_name': project_name,
			'project_pipeline': project_pipeline,
			'know_how': know_how,
			'other_source':other_source,
			'check':check,
			'message': message
		}).then(function(returnval){
			returnval = JSON.parse(returnval);
			if(returnval['status'] == 'OK'){
				//alert("Success outside")
				$(location).attr('href',returnval['return_link']+"success");
			} else {
				//alert("Failed outside")
				$(location).attr('href',returnval['return_link']+"failed");
			}
		});
	})
}

function contactFormAjaxBecome(){
	odoo.define('web.ajax2', function(require){
	'use strict'; 
	var ajax = require('web.ajax');
	
		var name = $('input[name="b_name"]').val()
		var email = $('input[name="b_email"]').val()
		var phone = $('input[name="b_phone"]').val()
		var company = $('input[name="b_company"]').val()
		var partner_type = $('select[name="b_partner_type"]').val()
		var know_how = $('select[name="b_know_how"]').val()
		var check = $('#b_check').is(':checked')
		if (check)
			check = 'Yes'
		else
			check = 'No'
		
		var other_source = '';
		
		if(know_how === 'Other')
			other_source = $('input[name="b_other_source"]').val()
		
		var message = $('textarea[name="b_message"]').val()
		
		var res = ajax.jsonRpc("/submit/become", 'call', {
			'name' : name,
			'email': email,
			'phone': phone,
			'company' : company,
			'partner_type' : partner_type,
			'know_how': know_how,
			'other_source':other_source,
			'check':check,
			'message': message
		}).then(function(returnval){
			returnval = JSON.parse(returnval);
			if(returnval['status'] == 'OK'){
				//alert("Success become")
				$(location).attr('href',returnval['return_link']+"success");
			} else {
				//alert("Failed become")
				$(location).attr('href',returnval['return_link']+"failed");
			}
		});
	})
}
