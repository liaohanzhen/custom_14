#See LICENSE file for full copyright and licensing details.


from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        partner = self.partner_id
        if partner.parent_id:
            partner = partner.parent_id
        if 'sale_order_customer' in create_accounts:
            types['receivable'] = True
        if config.use_separate_accounts:
            types['use_separate'] = True
        if config.add_number_to_partner_number:
            types['add_number'] = True        
        if config.use_separate_partner_numbers:
            if 'sale_order_customer_numbers' in create_accounts: 
                types['customer_number'] = True
        if types:
            accounts = self.env['res.partner'].create_accounts(partner, types) 
        return super(SaleOrder, self).action_confirm()

