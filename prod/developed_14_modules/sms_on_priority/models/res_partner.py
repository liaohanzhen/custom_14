# -*- coding: utf-8 -*-

import base64
from datetime import datetime

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #     @api.multi
    def send_sms_to_partner(self, record, template=None):
        # template = self.env.ref("sms_template_helpdesk_ticket",False)
        if not template:
            return
        default_mobile = template.from_mobile_verified_id
        if not default_mobile:
            default_mobile = self.env['sms.number'].search(
                [('mobile_number', '!=', False), ('account_id', '!=', False)], limit=1)
        if not default_mobile:
            return
        sms_subtype = self.env['ir.model.data'].get_object('sms_frame', 'sms_subtype')
        template_obj = self.env['sms.frame.template']
        message_obj = self.env['sms.message']
        attachments = []
        if template.media_id:
            attachments.append((template.media_filename, base64.b64decode(template.media_id)))
        for partner in self:
            if not partner.mobile:
                continue
            sms_rendered_content = template_obj.render_template(template.template_body, template.model_id.model,
                                                                record.id)
            my_sms = default_mobile.account_id.send_message(default_mobile.mobile_number, partner.mobile,
                                                            sms_rendered_content.encode('utf-8'),
                                                            template.model_id.model, record.id, template.media_id,
                                                            media_filename=template.media_filename)

            message_obj.create({'record_id': record.id,
                                'model_id': template.model_id.id,
                                'account_id': default_mobile.account_id.id,
                                'from_mobile': default_mobile.mobile_number,
                                'to_mobile': partner.mobile,
                                'sms_content': sms_rendered_content,
                                'status_string': my_sms.response_string,
                                'direction': 'O',
                                'message_date': datetime.utcnow(),
                                'status_code': my_sms.delivary_state,
                                'sms_gateway_message_id': my_sms.message_id,
                                'by_partner_id': self.env.user.partner_id.id})
            record.message_post(body=sms_rendered_content, subject="SMS Sent", message_type="comment",
                                subtype_id=sms_subtype.id, attachments=attachments, sms_number_id=default_mobile.id,
                                to_mobile=partner.mobile, partner_ids=[partner.id])

        return True
