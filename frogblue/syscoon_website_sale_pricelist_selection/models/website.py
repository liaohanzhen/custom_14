from odoo import models
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'
    
    def get_pricelist_available(self, show_visible=False):
        pricelists = super(Website, self).get_pricelist_available(show_visible=show_visible)
        if show_visible:
            user = self.env.user
            user_pricelist = user.partner_id.commercial_partner_id.property_product_pricelist
            if not user._is_public() and user_pricelist not in pricelists:
                pricelists = user_pricelist + pricelists
            
        return pricelists 