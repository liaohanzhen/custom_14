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
import odoo
from odoo import api, http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment_paypal_express.controllers.main import PaypalExpressRedirect
from odoo.addons.payment.controllers.portal import PaymentProcessing

import logging
_logger = logging.getLogger(__name__)

class PaypalExpressRedirect(PaypalExpressRedirect):

    def update_shipping_address(self, sale_order, trans_obj, shipping_address):
        public_user_id = request.website.partner_id.id
        partnerAddress = request.env['res.partner'].sudo()
        s_state = shipping_address.get('admin_area_1')
        partner = request.env.user.partner_id
        country_id = request.env['res.country'].search([('code','=',shipping_address.get('country_code'))], limit=1)
        country_id = country_id.id if country_id else None
        state = request.env['res.country.state'].search(['|',('code','=',s_state),('name','=ilike',s_state),('country_id','=',country_id)], limit=1)
        state_id = state.id if state else None
        city = shipping_address.get('admin_area_2')
        zip = shipping_address.get('postal_code')
        name = shipping_address.get('recipient_name')
        street = shipping_address.get('address_line_1')
        street2 = shipping_address.get('address_line_2')
        email = shipping_address.get('email')
        phone = shipping_address.get('phone')
        if partner.id != public_user_id:
            domain = [
                ('name','=',name),
                ('email','=',email),
                ('phone','=',phone),
                ('parent_id','=',partner.id),
                ('type','=','delivery'),
                ('street','=',street),
                ('street2','=',street2),
                ('city','=',city),
                ('zip','=',zip),
                ('state_id','=',state_id),
                ('country_id','=',country_id),
            ]
            address = partnerAddress.search(domain, limit=1)
            if not address:
                address = partnerAddress.create({
                    'name' : name,
                    'email' : email,
                    'phone' : phone,
                    'parent_id' : partner.id,
                    'type' : 'delivery',
                    'street' : street,
                    'street2' : street2,
                    'city' : city,
                    'state_id' : state.id if state else None,
                    'zip' : zip,
                    'country_id' : country_id,
                })
            if not sale_order.partner_shipping_id.id == address.id:
                sale_order.sudo().write({
                    'partner_shipping_id': address.id,
                })
            if trans_obj and trans_obj.partner_id.id == public_user_id:
                trans_obj.sudo().write({
                    'partner_id': address.id,
                })
        else:
            address = partnerAddress.create({
                'name' : name,
                'email' : email,
                'phone' : phone,
                'customer': True,
                'street' : street,
                'street2' : street2,
                'city' : city,
                'state_id' : state.id if state else None,
                'zip' : zip,
                'country_id' : country_id,
            })
            sale_order.sudo().write({
                'partner_id': address.id,
                'partner_invoice_id': address.id,
                'partner_shipping_id': address.id,
            })
            if trans_obj:
                trans_obj.sudo().write({
                    'partner_id': address.id,
                })

    @http.route(['/paypal/express/checkout/state',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_express_checkout_state(self, **post):
        shipping_address = {}
        try:
            purchase_units = post.get('purchase_units')
            payer = post.get('payer')
            phone_numbers = payer['phone']['phone_number']['national_number'] if payer and payer.get('phone') else None
            email_address = payer['email_address']
            shipping_address = purchase_units[0]['shipping']['address']
            recipient_name = purchase_units[0]['shipping']['name']['full_name']
            shipping_address.update({
                'email': email_address,
                'phone': phone_numbers,
                'recipient_name': recipient_name
            })
        except Exception as e:
            _logger.info("~~~~~~~~~~~~~Exception~~~~~~~~%r~~~~~~~~~~~~~~~",e)
        order = request.website.sale_get_order()
        if order:
            trans_id = request.session.get('sale_transaction_id',False)
            if not trans_id:
                trans_obj = sale_order.payment_tx_id
            else:
                trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id))
            self.update_shipping_address(order, trans_obj, shipping_address)
            request.session['sale_last_order_id'] = order.id
        return super(PaypalExpressRedirect, self).paypal_express_checkout_state(**post)

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/payment/transaction/',
        '/shop/payment/transaction/<int:so_id>',
        '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """

        public_paypal_checkout = kwargs.get('public_paypal_checkout',False)
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)

        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False
        if not public_paypal_checkout:
            assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        _logger.info("-----transaction.render_sale_button(order)------%r----",transaction.render_sale_button(order))

        return transaction.render_sale_button(order)

class PaypalExpressCheckout(http.Controller):

    @http.route(['/get/paypal/acquirer/details',], type='json', auth="public", methods=['POST'], website=True)
    def get_paypal_acquirer_details(self, **post):
        acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'paypal_express'),('state','!=','disabled')], limit=1)
        data = {
            'acquirer_id':acquirer.id if acquirer else False,
            'enable_pro':acquirer.product_paypal if acquirer else False,
            'enable_cart':acquirer.cart_paypal if acquirer else False,
        }

        return data

    @http.route(['/get/product/order/details',], type='json', auth="public", methods=['POST'], website=True)
    def get_product_order_details(self, **post):

        product_id = post.get('product_id')
        set_qty = post.get('add_qty')
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        sale_order.order_line.sudo().unlink()
        sale_order._cart_update(
            product_id=int(product_id),
            set_qty=set_qty,
        )
        request.session['sale_last_order_id'] = sale_order.id

        return {
            'sale_order': sale_order.id
        }
