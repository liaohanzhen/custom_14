# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        result = super(IrHttp, self).session_info()
        result['x_studio_field_3E2nL'] = dict(self.env['calendar.event']._fields_get('x_studio_field_3E2nL').selection)
        return result
