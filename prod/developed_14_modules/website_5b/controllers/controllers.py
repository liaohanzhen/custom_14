# -*- coding: utf-8 -*-
from odoo import http
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.sh_project_portfolio.controllers.main import project_portfolio
from odoo.exceptions import UserError
import base64
import json
import requests

class project_portfolio_url(project_portfolio):
    @http.route(['/projects'], auth='public', website=True)
    def portfolio(self, **post):
        cta = 'project'
        image = 'project'
        application = ''
        return http.request.render('website_5b.page_projects', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.project.5b'].sudo().search([('is_publish', '=', 'true')], order = "display_order, id asc"),
            'cta': cta,
            'image':image})
            
#Replace root routing default page.
class Website(Website):
    @http.route(auth='public')
    def index(self, data={}, **kw):
        super(Website, self).index(**kw)
        
        projects = http.request.env['website.project.5b'].sudo().search([('is_publish', '=', True)], order = "publish_date desc")
        option_vals = ""
        for project in projects:
            if project.p_lat:
                option_vals += "{"
                option_vals += "position : { lat : " + str(project.p_lat) + ", lng : " + str(project.p_lon) + " }, "
                option_vals += "content : '" + str(project.name) + "<br />" + str(project.project_address) + "'"
                option_vals += "},"
            
        option_vals = option_vals[:-1]
        
        data = {
            'contents':http.request.env['website.news.5b'].sudo().search([('is_publish', '=', True)], order = "publish_date desc", limit = 3),
            'projects':http.request.env['website.project.5b'].sudo().search([('is_publish', '=', True)], order = "publish_date desc"),
            'map_data':option_vals
        }
        return http.request.render('website_5b.page_home', data)

class Website5B(http.Controller):
    
    @http.route(['/team2'], auth='public', website=True)
    def team2(self, **kw):
        cta = 'team2'
        image = 'team2'
        application = ''
        return http.request.render('website_5b.page_team2', {
            'root': '/',
            'application':application,
            'all_employee':http.request.env['hr.employee'].sudo().search([('active', '=', 'true')], order = "x_display_order,id ASC"),
            'cta': cta,
            'image':image})
            
    @http.route(['/joinus'], auth='public', website=True)
    def joinus(self, **kw):
        cta = 'joinus'
        image = 'joinus'
        application = ''
        return http.request.render('website_5b.page_joinus', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', 'joinus'), ('is_publish', '=', 'true')]),
            'cta': cta,
            'image':image})
            
    @http.route(['/team'], auth='public', website=True)
    def team(self, **kw):
        cta = 'team'
        image = 'team'
        application = ''
        return http.request.render('website_5b.page_team', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', 'team'), ('is_publish', '=', 'true')]),
            'all_employee':http.request.env['hr.employee'].sudo().search([('active', '=', 'true')], order = "x_display_order,id ASC"),
            'cta': cta,
            'image':image})
            
    '''
    @http.route('/<string:urlpart>', auth='public', website=True)
    def dynamic(self, urlpart='', **kw):
        _logger.error("Dynamic Routing 1111111")
        cta = urlpart
        image = urlpart
        application = ''
        return http.request.render('website_5b.page_static', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', urlpart), ('is_publish', '=', 'true')]),
            'cta': cta,
            'image':image})
    '''
    
    @http.route(['/about','/aboutus'], auth='public', website=True)
    def about(self, **kw):
        cta = 'about'
        image = 'about'
        application = ''
        return http.request.render('website_5b.page_aboutus', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', 'about'), ('is_publish', '=', 'true')]),
            'cta': cta,
            'image':image})
            
    @http.route(['/projects','/project'], auth='public', website=True)
    def project(self, **kw):
        cta = 'project'
        image = 'project'
        application = ''
        return http.request.render('website_5b.page_projects', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.project.5b'].sudo().search([('is_publish', '=', 'true')], order = "display_order, id asc"),
            'cta': cta,
            'image':image})
            
    @http.route(['/solutions','/solution'], auth='public', website=True)
    def solution(self, **kw):
        cta = 'solution'
        image = 'solution'
        application = ''
        return http.request.render('website_5b.page_solutions', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', 'solutions'), ('is_publish', '=', 'true')]),
            'cta': cta,
            'image':image})
            
    @http.route('/news', auth='public', website=True)
    def news(self, **kw):
        cta = 'news'
        image = 'news'
        news_title = ''
        return http.request.render('website_5b.page_news', {
            'root': '/',
            'news_title':news_title,
            'contents':http.request.env['website.news.5b'].sudo().search([('is_publish', '=', True)], order = "publish_date desc"),
            'cta': cta,
            'image':image})
            
    @http.route('/news/<string:year>', auth='public', website=True)
    def news_article_year(self, year="", **kw):
        cta = 'news'
        image = 'news'
        news_title = ''
        try:
            searchDateStart = datetime.strptime(year+'-01-01', "%Y-%m-%d")
            searchDateEnd = datetime.strptime(str((int(year)+1))+'-01-01', "%Y-%m-%d")
            return http.request.render('website_5b.page_news', {
            'root': '/',
            'news_title':news_title,
            'year': year,
            'cta': cta,
            'contents':http.request.env['website.news.5b'].sudo().search([('is_publish', '=', True),('publish_date', '>=', searchDateStart),('publish_date', '<', searchDateEnd)], order = "publish_date desc"),
            'image':image})
        except ValueError:
            return http.request.render('website_5b.404', {'root': '/'})
            
    @http.route('/news/<string:year>/<string:article>', auth='public', website=True)
    def news_article(self, year="", article="", **kw):
        cta = 'news'
        image = 'news'
        news_title = article
        return http.request.render('website_5b.page_news', {
            'root': '/',
            'news_title':news_title,
            'cta': cta,
            'contents':http.request.env['website.news.5b'].sudo().search([('is_publish', '=', True),('link_url', '=', news_title)]),
            'image':image})
            
    @http.route('/media', auth='public', website=True)
    def media(self, **kw):
        cta = 'media'
        image = 'media'
        application = ''
        return http.request.render('website_5b.page_media', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.media.5b'].sudo().search([('is_publish', '=', True)], order = "display_order, id asc"),
            'cta': cta,
            'image':image})
            
    @http.route(['/careers', '/career'], auth='public', website=True)
    def careers(self, **kw):
        cta = 'careers'
        image = 'careers'
        application = ''
        return http.request.render('website_5b.page_careers', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.content.5b'].sudo().search([('link_url', '=', 'careers'), ('is_publish', '=', 'true')]),
            'cta': cta,
            'image':image})
            
    
    @http.route('/submit/careers', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def submit_career(self, **kw):
        firstname = kw['firstname']
        lastname = kw['lastname']
        email = kw['email']
        phone = kw['phone']
        team = kw['relevant_team']
        
        _checked = 'No'
        if kw.get('check_5b',False):
            _checked = 'Yes'
                
        message = kw['message']
        
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
        link_url = '/submit/careers/'
        return_link = base_url + link_url
        
        attachment_id = None
        name = ""
        attachment = ""
        
        if kw.get('resume',False):
            Attachments = request.env['ir.attachment']
            name = kw.get('resume').filename
            file = kw.get('resume')
            attachment = file.read()
            attachment1 = base64.b64encode(attachment)
            attachment_id = Attachments.sudo().create({
                'name':name,
                'res_name': '',
                'type': 'binary',
                'datas': attachment1,
            })
            value = {
                'attachment' : attachment_id
            }
            
        full_name = str(firstname.capitalize()) + " " + str(lastname.capitalize())
        
        msg_body = """Name: %s <br />
        Phone: %s<br />
        Email: %s<br />
        Relevant team: %s<br />
        Like to hear about 5B update?: %s<br />
        Message: <br /><br />%s""" %(full_name, phone, email, team, _checked, message)
        
        if _checked == 'Yes':
            vals = {
                'name':full_name,
                'company_name': '',
                'email': email,
                #'is_email_valid':'t'
            }
            self.create_maillist(vals,'Opted into mailing list')
            
        email_to = 'recruitment@5b.com.au'
        email_from = email
        email_cc = 'info@5b.com.au'
        
        template_data = {
            'subject': 'Career Profile :: ' + str(full_name),
            'body_html': msg_body,
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': email_cc,
            'attachment_ids':[(4,attachment_id.id)]
            }
        self.send_email_fn(template_data)
        
        return http.redirect_with_hash(return_link+'success')
        
        
    @http.route(['/contact','/contactus'], auth='public', website=True)
    def contact(self, **kw):
        cta = 'contact'
        image = 'contact'
        application = ''
        country = request.env['res.country'].sudo().search([])
        source = request.env['utm.source'].sudo().search([])
        return http.request.render('website_5b.page_contact', {
            'root': '/',
            'application':application,
            'cta':cta,
            'country':country,
            'source':source,
            'image':image})
            
    @http.route('/submit/<string:page>/success', auth='public', website=True)
    def submit_success(self, page='', **kw):
        cta = 'contact'
        image = 'contact'
        application = ''
        return http.request.render('website_5b.page_submit_success', {
            'root': '/',
            'application':application,
            'cta': cta,
            'page':page,
            'image':image})
            
    @http.route('/submit/<string:page>/failed', auth='public', website=True)
    def submit_failed(self, page='', **kw):
        cta = 'contact'
        image = 'contact'
        application = ''
        return http.request.render('website_5b.page_submit_failed', {
            'root': '/',
            'application':application,
            'cta': cta,
            'page':page,
            'image':image})
            
    @http.route('/submit/contact', type='json', auth="public", website=True)
    def get_contact_form(self, **kw):
        name = kw['name']
        email = kw['email']
        phone = kw['phone']
        company = kw['company']
        c_type = kw['type']
        subject = kw['subject']
        message = kw['message']
        know_how = kw['know_how']
        check = kw['check']
        
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
        link_url = '/submit/contact/'
        return_link = base_url + link_url
        
        msg_body = """Name: %s <br />
        Phone: %s<br />
        Email: %s<br />
        Company: %s<br />
        Contact type: %s<br />
        Know how?: %s<br />
        Like to hear about 5B update?: %s<br />
        Subject: %s <br /><br />%s""" %(name, phone, email, company, c_type, know_how, check, subject, message)
        
        email_to = 'info@5b.com.au'
        if c_type == 'career':
            email_to = 'recruitment@5b.com.au'
        if c_type == 'media':
            email_to = 'marketing@5b.com.au'
        if c_type == 'account':
            email_to = 'accounts@5b.com.au'
        email_from = email
        email_cc = 'info@5b.com.au'
        
        
        template_data = {
            'subject': 'Website contact form :: ' + str(name),
            'body_html': msg_body,
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': email_cc
            }
        self.send_email_fn(template_data)
        
        if check == 'Yes':
            vals = {
                'name':name,
                'company_name': company,
                'email': email,
                #'is_email_valid':'t'
            }
            self.create_maillist(vals,'Opted into mailing list')
        
        if email_to == 'info@5b.com.au':
            # create a lead in erp
            #-------------------------------------
            
            country_id = request.env['res.country'].sudo().search([('name','=','Australia')])
            _cid= country_id.id
            
            source_id = request.env['utm.source'].sudo().search([('name','=','5B Website')]).id
            
            _lead_data = {
                'name': 'Website contact :: ' + str(subject),
                'contact_name': name,
                'partner_name': company,
                'country_id': _cid,
                'type': 'lead',
                'source_id': source_id,
                'user_id': request.env.uid,
                'email_from': email_from,
                'phone': phone,
                'description': message
            }
            #self.send_to_lead(_lead_data)
            _create_obj = request.env['crm.lead']
            _create_id = _create_obj.sudo().create(_lead_data)
        
        result = {
            'status':'OK', 
            'message':'',
            'return_link':return_link
        }
        return (json.dumps(result))
        
    @http.route('/submit/outside', type='json', auth="public", website=True)
    def get_contact_form_outside(self, **kw):
        name = kw['name']
        email = kw['email']
        phone = kw['phone']
        company = kw['company']
        company_role = kw['company_role']
        website = kw['website']
        country = kw['country']
        company_type = kw['company_type']
        project_name = kw['project_name']
        project_pipeline = kw['project_pipeline']
        #address = kw['address']
        #city = kw['city']
        message = kw['message']
        know_how = kw['know_how']
        check = kw['check']
        
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
        link_url = '/submit/contact/'
        return_link = base_url + link_url
        
        msg_body = """Name: %s <br />
        Phone: %s<br />
        Email: %s<br />
        Role with the company: %s<br />
        Company: %s<br />
        Company type: %s<br />
        Website: %s<br />
        Project name: %s<br />
        Project pipeline: %s<br />
        Country: %s<br />
        Know how?: %s<br />
        Like to hear about 5B update?: %s<br />
        Message:<br /><br />%s""" %(name, phone, email, company_role, company, company_type, website, project_name, project_pipeline, country, know_how, check, message)
        
        email_to = 'info@5b.com.au'
        email_from = email
        email_cc = 'info@5b.com.au'
        
        template_data = {
            'subject': 'Website contact outside Australia :: ' + str(name),
            'body_html': msg_body,
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': email_cc
            }
        self.send_email_fn(template_data)
        if check == 'Yes':
            vals = {
                'name':name,
                'company_name': company,
                'email': email,
                #'is_email_valid':'t'
            }
            self.create_maillist(vals,'Opted into mailing list')
            
        # create a lead in erp
        #-------------------------------------
        _cid = 'NULL'
        if country:
            country_id = request.env['res.country'].sudo().search([('name','=',country)])
            _cid= country_id.id
        
        source_id = request.env['utm.source'].sudo().search([('name','=','5B Website')]).id
            
        #_logger.error("Country ID ["+str(_cid)+"]["+str(country)+"]")
        _lead_description = "Company type: %s\nProject portfolio: %s MW\nPipeline of project: %s\n\n%s" %(company_type, project_name, project_pipeline, message)
        _lead_data = {
            'name': 'Website contact outside Australia :: ' + str(name),
            'contact_name': name,
            'partner_name': company,
            'website': website,
            'country_id': _cid,
            'type': 'lead',
            'source_id':source_id,
            'user_id': request.env.uid,
            'email_from': email,
            'function': company_role,
            'phone': phone,
            'description': _lead_description,
        }
        #self.send_to_lead(_lead_data)
        _create_obj = request.env['crm.lead']
        _create_id = _create_obj.sudo().create(_lead_data)
        
        result = {
            'status':'OK', 
            'message':'',
            'return_link':return_link
        }
        return (json.dumps(result))
        
    @http.route('/submit/become', type='json', auth="public", website=True)
    def get_contact_form_become(self, **kw):
        name = kw['name']
        email = kw['email']
        phone = kw['phone']
        company = kw['company']
        partner_type = kw['partner_type']
        message = kw['message']
        know_how = kw['know_how']
        check = kw['check']
        
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
        link_url = '/submit/become/'
        return_link = base_url + link_url
        
        msg_body = """Name: %s <br />
        Phone: %s<br />
        Email: %s<br />
        Company: %s<br />
        Partner type: %s<br />
        Know how?: %s<br />
        Like to hear about 5B update?: %s<br />
        Message:<br /><br />%s""" %(name, phone, email, company, partner_type, know_how, check, message)
        
        email_to = request.env['ir.config_parameter'].sudo().get_param('website.become.partner.email.to')
        if not email_to:
            email_to = 'info@5b.com.au'
        email_from = email
        email_cc = 'info@5b.com.au'
        
        template_data = {
            'subject': 'Become a partner :: ' + str(name),
            'body_html': msg_body,
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': email_cc
            }
        self.send_email_fn(template_data)
        
        if check == 'Yes':
            vals = {
                'name':name,
                'company_name': company,
                'email': email,
                #'is_email_valid':'t'
            }
            self.create_maillist(vals,'Opted into mailing list')
        
        result = {
            'status':'OK', 
            'message':'',
            'return_link':return_link
        }
        return (json.dumps(result))
        
    def send_email_fn(self,template_data):
        
        if template_data:
            template_obj = request.env['mail.mail']
            template_id = template_obj.sudo().create(template_data)
            template_id.sudo().send()
        
        return True
    
    def create_maillist(self, _createval, _listname):
        rel_id = None
        mail_list_contact = request.env['mailing.contact']
        contact_id = mail_list_contact.sudo().search([('name', '=', _createval['name']), ('company_name', '=', _createval['company_name']), ('email', '=', _createval['email'])], limit =1)
        if not contact_id:    
            contact_id = mail_list_contact.sudo().create(_createval)
        if contact_id:
            list_id = request.env['mailing.list'].sudo().search([('name', '=', _listname)]).id
            sql = "select 1 from mailing_contact_list_rel where contact_id='{}' and   list_id ='{}' ".format(contact_id.id, list_id)
            request.env.cr.execute(sql)
            rows = request.env.cr.fetchall()
            if len(rows) == 0:
                sql ="insert into mailing_contact_list_rel(contact_id,list_id)  values('{}','{}')".format(contact_id.id, list_id)
                request.env.cr.execute(sql)
                
    '''
    def create_maillist(self, _createval, _listname):
        rel_id = None
        mail_list_contact = request.env['mailing.contact']
        contact_id = mail_list_contact.sudo().create(_createval)
        
        if contact_id:
            list_id = http.request.env['mailing.list'].sudo().search([('name', '=', _listname)]).id
            mail_list_contact_rel = request.env['mailing_contact_list_rel']
            vals = {
                'contact_id':contact_id.id,
                'list_id':list_id
            }
            rel_id = mail_list_contact_rel.sudo().create(vals)
    '''
    
    @http.route('/submit/subscription', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def submit_email_subscription(self, **kw):
        firstname = kw['firstname']
        email = kw['email']
        company = kw['company']
        lastname = kw['lastname']
                
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
        link_url = '/submit/subscription/'
        return_link = base_url + link_url
        
        full_name = str(firstname.capitalize()) + " " + str(lastname.capitalize())
        
        vals = {
            'name':full_name,
            'company_name': company,
            'email': email,
            #'is_email_valid':'t'
        }
        self.create_maillist(vals, 'Subscribe to 5B email updates')
        return http.redirect_with_hash(return_link+'success')
        
    @http.route(['/faqs','/faq'], auth='public', website=True)
    def faqs(self, **kw):
        cta = 'faqs'
        image = 'faqs'
        application = ''
        return http.request.render('website_5b.page_faqs', {
            'root': '/',
            'application':application,
            'contents':http.request.env['website.faqs.5b'].sudo().search([('is_publish', '=', True)], order = "display_order, id asc"),
            'cta': cta,
            'image':image})
    