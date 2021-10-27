from odoo import fields,models

class SyscomCategory(models.Model):
    _name = 'syscom.category'
    
    syscom_id = fields.Integer("Syscom Id")
    name = fields.Char("Name")
    syscom_level = fields.Integer("Syscom Level")
    
    