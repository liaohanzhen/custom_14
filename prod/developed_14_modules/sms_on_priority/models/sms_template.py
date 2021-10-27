# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import Warning


class SmsTemplate(models.Model):
    _inherit = "sms.frame.template"

    #     @api.multi
    def unlink(self):
        helpdesk_template = self.env.ref("sms_on_priority.helpdesk_ticket_template", False)
        if helpdesk_template and helpdesk_template.id in self.ids:
            raise Warning("You can't delete template %s. Its default template used for Helpdesk ticket sms." % (
                helpdesk_template.name))

        return super(SmsTemplate, self).unlink()
