# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _check_company_auto = False

    company_id = fields.Many2one('res.company', 'Company', required=True, store=True, index=True, check_company=False)

    def write(self, vals):
        res = super(ProductionLot, self).write(vals)
        return res