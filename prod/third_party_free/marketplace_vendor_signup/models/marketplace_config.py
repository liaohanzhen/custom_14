# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    multi_step_signup = fields.Boolean(string="Multi Step Signup", related="website_id.mp_multi_step_signup",readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'multi_step_signup', self.multi_step_signup)
        return True

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        multi_step_signup = self.env['ir.default'].get('res.config.settings', 'multi_step_signup')
        res.update(
            multi_step_signup = multi_step_signup,
        )
        return res
