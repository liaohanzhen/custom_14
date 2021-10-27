# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
#from odoo.addons.website_sale.controllers.main import WebsiteSale
#from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import registry as registry_get
from odoo.api import Environment
from odoo import SUPERUSER_ID
import werkzeug
from odoo.http import request

from odoo.tools.misc import get_lang

#import sys
#reload(sys)  
#sys.setdefaultencoding('utf8')
class EquipmentBooking(http.Controller):
    
    @http.route('/calendar/equipment/accept', type='http', auth="calendar")
    def accept(self, db, token, action, id, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['calendar.event'].search([('access_token', '=', token)])
            if attendee:
                attendee.do_accept()
        return self.view(db, token, action, id, view='form')
    
    @http.route('/calendar/equipment/decline', type='http', auth="calendar")
    def declined(self, db, token, action, id):
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['calendar.event'].search([('access_token', '=', token)])
            if attendee:
                attendee.do_decline()
        return self.view(db, token, action, id, view='form')
    
    @http.route('/calendar/equipment/view/', type='http', auth="calendar",website=True)
    def view(self, db, token, action, id, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            event = env['calendar.event'].search([('access_token', '=', token)])
            if not event:
                return request.not_found()
            if request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
                return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event' % (db, id))
            files = event._get_ics_file()
            content = files[event.id]
            return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event' % (db, id))
            
    @http.route('/portal/delivery_equipment/', auth='public', website=True)
    def index(self, **kw):
        val={
                'res_partners': http.request.env['res.partner'].sudo().search([])
            }
        return http.request.render('delivery_equipment_booking.index',val)
    @http.route('/booking-thank-you',type="http", auth="public", csrf=False, website=True)
    def my_portal_delivery_equipment_Booking(self, **kwargs):
        
        partner_id = kwargs.get('partner_id',False)
        partner_making_book = kwargs.get('partner_making_book',False)
        department_name = kwargs.get('department_name',False)
        entered_firm = kwargs.get('entered_firm',False)
        delivery_provide_details = kwargs.get('delivery_provide_details',False)
        provide_referance_number = kwargs.get('provide_referance_number',False)
        start_date_time = kwargs.get('start_date_time',False)
        event_date_time = kwargs.get('event_date_time',False)
        questions_comments = kwargs.get('questions_comments',False)
        event_title = kwargs.get('event_title',False)
        event_description = kwargs.get('event_description',False)
        selection_booking_ids =[] 
        request_refer_ids = []
        requirements_ids = []
        for data,value in kwargs.items():
            if data in ['delivery','pickup','equipment_only','delivery_pickup_eqpt','stock_movement','stock_movement','section_booking']:
                request_refer_id = http.request.env['request.refer'].sudo().search([('name','=',value)])
                request_refer_ids.append(request_refer_id.id)
            if data in ['mavpod','selection_a','selection_b','selection_c','storage','drive_way']:
                selection_booking_id = http.request.env['selection.booking'].sudo().search([('name','=',value)])
                selection_booking_ids.append(selection_booking_id.id)    
            if data in ['time_critical','clear_driveway','forklift_2_5t','forklift_6t','pallet_jack','tool_kit','drill_press','band_saw','welder','other_discribe'
                        'labor_assistance','factory_floor_space','inform_requester']:
                requirements_id = http.request.env['requirements'].sudo().search([('name','=',value)])
                requirements_ids.append(requirements_id.id)        
        
        vals={'name':event_title,'partner_id_equipment':int(partner_id) or False,
              'partner_making_book':partner_making_book,'department_name':department_name,
              'start':start_date_time,'stop':event_date_time,
              #'start_datetime':start_date_time,'end_datetime':event_date_time,
              'entered_firm':entered_firm,'delivery_provide_details':delivery_provide_details,
              'provide_referance_number':provide_referance_number,
              'questions_comments':questions_comments,'event_title':event_title,'description':event_description,
              'selection_booking_ids':[(6,0,selection_booking_ids or [])], 
              'request_refer_ids':[(6,0,request_refer_ids or [])],
              'requirements_ids':[(6,0,requirements_ids or [])],
              }
        calendar_event_id = http.request.env['calendar.event'].sudo().create(vals)
        
        temp_id = http.request.env.ref("delivery_equipment_booking.delivery_equipment_booking_email_to_customer")
        if temp_id:
#             template_obj = http.request.env['mail.template']
            #temp_id.sudo().send_mail(calendar_event_id.id, force_send=True)
            calendar_event_id.sudo()._send_mail_to_attendees('delivery_equipment_booking.delivery_equipment_booking_email_to_customer')
        return http.request.render('delivery_equipment_booking.booking-thank-you')
   