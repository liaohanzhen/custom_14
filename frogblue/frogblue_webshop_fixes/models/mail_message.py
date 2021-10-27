from odoo import models

class MailMessage(models.Model):
    _inherit='mail.message'
    
    def _portal_message_format(self, fields_list):
        vals_list = self._message_format(fields_list)
        for vals in vals_list:
            if vals.get('author_id'):
                partner = self.env['res.partner'].sudo().browse(vals.get('author_id')[0])
                vals['author_id'] = (partner.id, ''.join([name and name[0].capitalize() for name in partner.name.split(' ')])) 
        return vals_list