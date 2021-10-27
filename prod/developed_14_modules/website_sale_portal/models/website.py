
from odoo import models, api

class Menu(models.Model):
    _inherit = "website.menu"
    
    def _compute_visible(self):
        for menu_id in self:
            if menu_id.url=='/shop' and self.env.user == self.env.ref('base.public_user'):
                menu_id.is_visible=False
            else:
                super(Menu, self)._compute_visible()