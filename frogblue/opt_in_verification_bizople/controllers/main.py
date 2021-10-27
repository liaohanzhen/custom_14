# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import http
from odoo.http import route, request
from odoo.addons.website_mass_mailing.controllers.main import MassMailController
import json
import urllib
from odoo.addons.http_routing.models.ir_http import slug, unslug


class NewsLetterSubscription(http.Controller):
    @http.route('/user-opt-in', type='http', auth="public",
                website=True)
    def user_subscribe_newsletter(self, **post):
        update = True
        if 'contact' in post and post['contact']:
            contacts = request.env['mailing.contact'].sudo().search([('contact_uniq_number', '=', post['contact'].split())])
            if not contacts:
                update = False
            for contact in contacts:
                contact.sudo().subscription_list_ids.opt_out = False
        else:
            update = False
        if update:
            return request.redirect("/subscribe-thank-you")
        else:
            return request.redirect("/404")


class MassMailController(MassMailController):

    @route('/website_mass_mailing/subscribe', type='json', website=True, auth="public")
    def subscribe(self, list_id, email, **post):
        list_val = request.env['mailing.contact'].sudo().browse(int(list_id))

        # link = "/user-opt-in/%s" % slug(obj)
        Contacts = request.env['mailing.contact'].sudo()
        name, email = Contacts.get_name_email(email)
        contact_ids = Contacts.search([
            ('list_ids', 'in', [int(list_id)]),
            ('email', '=', email),
        ], limit=1)
        opt_in_template = request.env.ref("opt_in_verification_bizople.email_template_news_opt_in_mail")
        if not contact_ids:
            # inline add_to_list as we've already called half of it
            new_contact = Contacts.create({'name': name, 'email': email, 'list_ids': [(6, 0, [int(list_id)])]})
            # new_contact.opt_out = True
            for line in new_contact.subscription_list_ids:
                if line.list_id.id == list_id:
                    line.opt_out = True
            website_partner = new_contact
            contact_obj = new_contact
        else:
            contact_obj = contact_ids[0]
            website_partner = contact_ids
            for contract in contact_ids:
                for line in contract.subscription_list_ids:
                    if line.list_id.id == list_id:
                        line.opt_out = True
        url_link = "/user-opt-in/mail/%s/contact/%s" % (slug(list_val), slug(contact_obj))
        ip_address = http.request.httprequest.remote_addr
        city_name = ""
        country_name = ""
        try:
            urlFoLaction = "http://www.freegeoip.net/json/{0}".format(
                ip_address)
            locationInfo = json.loads(urllib.request.urlopen(urlFoLaction).read().decode("utf-8"))
            country_name = locationInfo['country_name']
            city_name = locationInfo['city']
        except:
            pass
        if website_partner:
            opt_in_template.sudo().send_mail(website_partner.id, force_send=True)
            website_partner.ip_address = ip_address
            website_partner.city_name = city_name
            website_partner.country_name = country_name
        
        # add email to session
        request.session['mass_mailing_email'] = email
        return True
