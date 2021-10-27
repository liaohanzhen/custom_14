# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
import uuid
class Meeting(models.Model):
    """ Model for Calendar Event
    """

    _inherit = 'calendar.event'
    
    def _default_access_token(self):
        return uuid.uuid4().hex
    
    selection_booking_ids = fields.Many2many('selection.booking',string="Selection Booking") 
    request_refer_ids = fields.Many2many('request.refer',string="What does this request refer to?")
    requirements_ids = fields.Many2many('requirements',string="Requirements")
    partner_email =  fields.Char(string="Email address")
    partner_making_book = fields.Char(string="Name of person making the booking")
    department_name = fields.Char(string="Name of the department")
    request_refer = fields.Char(string="What does this request refer to?")
    entered_firm = fields.Selection([('firm','Firm'),('indicative_unlike','Indicative (unlikely to change)'),('indicative_like','Indicative (likely to change)')],string="Are the dates & time entered firm or indicative?")
    delivery_provide_details = fields.Text(string="In case of delivery please provide details of the delivery. (size, weight, project)")
    provide_referance_number =  fields.Char(string="Provide a reference number")
    questions_comments = fields.Text(string="Questions and Comments")
    event_title = fields.Char(string="Event title")
    event_description = fields.Text(string="Event Description")
    partner_id_equipment = fields.Many2one('res.partner',string="Task assigned to")
    access_token = fields.Char('Invitation Token', default=_default_access_token)
    
    def do_accept(self):
        """ Marks event invitation as Accepted. """
        #result = self.write({'state': 'open'})
        for event in self:
            event.message_post(
                body=_("%s has accepted invitation") % (event.name),
                subtype_xmlid="calendar.subtype_invitation")
        temp_id = self.env.ref("delivery_equipment_booking.delivery_equipment_booking_accepted")
        if temp_id:
            temp_id.send_mail(self.id,force_send=True)
        return True

    def do_decline(self):
        """ Marks event invitation as Declined. """
        #res = self.write({'state': 'draft'})
        for event in self:
            event.message_post(body=_("%s has declined invitation") % (event.name), subtype="calendar.subtype_invitation")
        temp_id = self.env.ref("delivery_equipment_booking.delivery_equipment_booking_rejected")
        if temp_id:
            temp_id.send_mail(self.id,force_send=True)    
        return True
    
    def _send_mail_to_attendees(self, template_xmlid, force_send=False, force_event_id=None):
        """ Send mail for event invitation to event attendees.
            :param template_xmlid: xml id of the email template to use to send the invitation
            :param force_send: if set to True, the mail(s) will be sent immediately (instead of the next queue processing)
        """
        res = False

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        # get ics file for all meetings
        #ics_files = force_event_id._get_ics_file() if force_event_id else self.mapped('event_id')._get_ics_file()

        # prepare rendering context for mail template
        colors = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }
        rendering_context = dict(self._context)
        rendering_context.update({
            'color': colors,
            'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
            'dbname': self._cr.dbname,
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069'),
            'force_event_id': force_event_id,
            'modelname':self._name,
        })
        invitation_template = invitation_template.with_context(rendering_context)

        # send email with attachments
        mails_to_send = self.env['mail.mail']
        for event in self:
            if event.partner_id_equipment.email:
                # FIXME: is ics_file text or bytes?
                #event_id = force_event_id.id if force_event_id else attendee.event_id.id
                #ics_file = ics_files.get(event_id)
                mail_id = invitation_template.send_mail(event.id, notif_layout='mail.mail_notification_light')

                vals = {}
#                 if ics_file:
                vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                      'mimetype': 'text/calendar',
                                                      'datas_fname': 'invitation.ics',
#                                                       'datas': base64.b64encode(ics_file)
                                                      })]
                vals['model'] = None  # We don't want to have the mail in the tchatter while in queue!
                vals['res_id'] = False
                current_mail = mails_to_send.browse(mail_id)
                res = current_mail.sudo().send()

        
            

        return True
