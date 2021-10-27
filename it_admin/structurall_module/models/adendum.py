from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class Adendum(models.Model):
    _name = 'adendum.adendum'
    _description = 'Adendum Structurall'
    _rec_name ='name'

    name = fields.Char("Name", required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    no_adendum = fields.Integer(string="No. adendum")
    
    partner_id = fields.Many2one('res.partner',string="Cliente")
    fecha_inicial = fields.Date(string="Fecha inicial")
    fecha_final = fields.Date(string="Fecha final")
    no_meses = fields.Float(string="Número de meses")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
    default=lambda self: self.env['res.company']._company_default_get('account.invoice'))

    adendum_origen = fields.Many2one('contract.contract',string="Origen")


    #Estados
    state = fields.Selection([
            ('draft', 'Borrador'),
            ('done', 'Validado')
            ],default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('adendum.adendum') or _('New')
        result = super(Adendum, self).create(vals)
        return result

    def validar_adendum(self):
        self.write({'state': 'done'})
        self.adendum_origen.write({'date_end':self.fecha_final})

