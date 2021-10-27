# -*- coding: utf-8 -*-


from odoo import models
from odoo.osv import expression


class AmazonPayPaymentIrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_domain(cls):
        domain = super()._get_translation_frontend_modules_domain()
        return expression.OR([domain, [('name', '=', 'payment_amazonpay')]])

