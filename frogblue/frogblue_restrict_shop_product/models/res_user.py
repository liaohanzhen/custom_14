from odoo import fields,models



class ResUsers(models.Model):
    _inherit='res.users'
    
    
    shop_preview_user=fields.Boolean("Shop Preview User")