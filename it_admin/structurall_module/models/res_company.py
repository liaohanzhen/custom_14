# -*- coding: utf-8 -*-


from odoo import fields, models,api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    dias_gracia =  fields.Integer(string='Dias de gracia', store=True)
