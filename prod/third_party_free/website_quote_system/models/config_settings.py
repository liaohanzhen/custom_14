# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models,fields,api,_

class CustQuoteConfiguration(models.TransientModel):

    _name="customer.quote.settings"
    _inherit="res.config.settings"
    _description = "Customer Quote Settings"

    notify_admin_on_new_quote = fields.Boolean(string='Enable to notify to admin')
    notify_salesman_on_new_quote = fields.Boolean(string = 'Enable to notify to salesman')
    notify_customer_on_new_quote = fields.Boolean(string='Enable to notify to customer')
    salesman_id = fields.Many2one('res.users',string="This Salesman will be used to send mail if no salesman is assigned to the new quotation created.")
    notify_customer_on_quote_state_change = fields.Boolean(string = 'Customer')
    allow_customer_to_quote_price = fields.Boolean(string="Can customer propose quote prices", default=True)

    def set_values(self):
        super(CustQuoteConfiguration, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.sudo().set('customer.quote.settings','notify_admin_on_new_quote', self.notify_admin_on_new_quote)
        IrDefault.sudo().set('customer.quote.settings','notify_customer_on_new_quote', self.notify_customer_on_new_quote)
        IrDefault.sudo().set('customer.quote.settings','notify_salesman_on_new_quote', self.notify_salesman_on_new_quote)
        IrDefault.sudo().set('customer.quote.settings','salesman_id', self.salesman_id.id)
        IrDefault.sudo().set('customer.quote.settings','notify_customer_on_quote_state_change', self.notify_customer_on_quote_state_change)
        IrDefault.sudo().set('customer.quote.settings','allow_customer_to_quote_price', self.allow_customer_to_quote_price)
        IrDefault.sudo().set('customer.quote.settings','notify_admin_on_new_quote_m_tmpl_id', self.notify_admin_on_new_quote_m_tmpl_id.id)
        IrDefault.sudo().set('customer.quote.settings','notify_customer_on_new_quote_m_tmpl_id', self.notify_customer_on_new_quote_m_tmpl_id.id)
        IrDefault.sudo().set('customer.quote.settings','notify_salesman_on_new_quote_m_tmpl_id', self.notify_salesman_on_new_quote_m_tmpl_id.id)
        IrDefault.sudo().set('customer.quote.settings','notify_customer_on_quote_state_change_m_tmpl_id', self.notify_customer_on_quote_state_change_m_tmpl_id.id)

        return True

    @api.model
    def get_values(self):
        res = super(CustQuoteConfiguration, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        notify_admin_on_new_quote= IrDefault.get('customer.quote.settings','notify_admin_on_new_quote')
        notify_customer_on_new_quote = IrDefault.get('customer.quote.settings','notify_customer_on_new_quote')
        notify_salesman_on_new_quote= IrDefault.get('customer.quote.settings','notify_salesman_on_new_quote')
        salesman_id= IrDefault.get('customer.quote.settings','salesman_id')
        notify_customer_on_quote_state_change= IrDefault.get('customer.quote.settings','notify_customer_on_quote_state_change')
        allow_customer_to_quote_price= IrDefault.get('customer.quote.settings','allow_customer_to_quote_price')
        notify_admin_on_new_quote_m_tmpl_id = IrDefault.get('customer.quote.settings','notify_admin_on_new_quote_m_tmpl_id')
        notify_customer_on_new_quote_m_tmpl_id = IrDefault.get('customer.quote.settings','notify_customer_on_new_quote_m_tmpl_id')
        notify_salesman_on_new_quote_m_tmpl_id = IrDefault.get('customer.quote.settings','notify_salesman_on_new_quote_m_tmpl_id')
        notify_customer_on_quote_state_change_m_tmpl_id = IrDefault.get('customer.quote.settings','notify_customer_on_quote_state_change_m_tmpl_id')
        res.update({
            'notify_admin_on_new_quote': notify_admin_on_new_quote,
            'notify_salesman_on_new_quote': notify_salesman_on_new_quote,
            'salesman_id':salesman_id,
            'notify_customer_on_quote_state_change': notify_customer_on_quote_state_change,
            'allow_customer_to_quote_price':allow_customer_to_quote_price,
            'notify_admin_on_new_quote_m_tmpl_id':notify_admin_on_new_quote_m_tmpl_id,
            'notify_salesman_on_new_quote_m_tmpl_id':notify_salesman_on_new_quote_m_tmpl_id,
            'notify_customer_on_quote_state_change_m_tmpl_id':notify_customer_on_quote_state_change_m_tmpl_id,
            'notify_customer_on_new_quote': notify_customer_on_new_quote,
            'notify_customer_on_new_quote_m_tmpl_id': notify_customer_on_new_quote_m_tmpl_id,
        })
        return res

    notify_admin_on_new_quote_m_tmpl_id = fields.Many2one(
        "mail.template", string="New Quote Request Mail to Admin", domain="[('model_id.model','=','quote.quote')]")
    notify_customer_on_new_quote_m_tmpl_id = fields.Many2one(
    "mail.template", string="New Quote Request Mail to Customer", domain="[('model_id.model','=','quote.quote')]")
    notify_salesman_on_new_quote_m_tmpl_id = fields.Many2one(
        "mail.template", string="New Quote Request Mail to Salesman", domain="[('model_id.model','=','quote.quote')]")
    notify_customer_on_quote_state_change_m_tmpl_id = fields.Many2one(
        "mail.template", string="Quote Status Change Mail to Customer", domain="[('model_id.model','=','quote.quote')]")
