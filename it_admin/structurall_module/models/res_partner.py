from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    autoizar_con_saldo_vencido = fields.Boolean(string='Autorizar con saldo vencido')

    sales_teams = fields.Many2many('crm.team',string="Equipos de venta permitidos")
    