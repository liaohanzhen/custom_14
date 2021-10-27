from odoo import fields, models, api, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'


    nombre_legal = fields.Char(string="Nombre del representante legal")
    direccion = fields.Text(string="Lugar")
    estados = fields.Many2many('res.country.state', string="Estados")

    #Campos Poder notarial
    nombre_representante_st = fields.Char(string="Nombre del representante legal")
    testimonio_notarial_st = fields.Char(string="Testimonio notarial")
    fecha_st = fields.Date(string="Fecha")
    notaria_st = fields.Char(string="Notaria")
    nombre_notario_st = fields.Char(string="Nombre del notario")
    domicilio_st = fields.Char(string="Domicilio")
    ciudad_notario_st = fields.Char(string="Ciudad del notario")
    