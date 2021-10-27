# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        no_color = ['status3', 'SAV OK']
        result = super(IrHttp, self).session_info()
        selection = dict(
            self.env['calendar.event'].fields_get('x_studio_field_3E2nL')['x_studio_field_3E2nL']['selection'])
        for i in no_color: selection.pop(i)
        result['allow_back_color'] = selection
        return result

