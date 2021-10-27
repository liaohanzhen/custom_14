from odoo import fields,models

class SyscomBrand(models.Model):
    _name = 'syscom.brand'
    
    syscom_id = fields.Char("Syscom Id")
    name = fields.Char("Name")