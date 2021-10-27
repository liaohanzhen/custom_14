# -*- coding: utf-8 -*-
############################################################################
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
############################################################################

from odoo.addons.website_sale.controllers.main import WebsiteSaleForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class CustomerQuote(http.Controller):

    @http.route(['/shop/customer_quote'], type='json',  methods=['POST'], auth="public", website=True)
    def customer_quote_modal(self, product_id, **kw):
        allow_customer_to_quote_price = request.env['ir.default'].sudo().get('customer.quote.settings', 'allow_customer_to_quote_price')
        obj = request.env['product.product'].sudo().browse([product_id])
        temp_id = request.env['ir.ui.view']._render_template("website_quote_system.customer_quote_template", {
            'prod_id': obj.id,
            'prod_img': obj.image_128,
            'prod_minqty': obj.min_qty,
            'prod_name': obj.name,
            'prod_price': obj._get_combination_info_variant().get('price'),
            'prod_variant': obj.product_template_attribute_value_ids,
            'product_uom_id_name': obj.uom_id.name,
            'allow_customer_to_quote_price': allow_customer_to_quote_price,
        })
        return temp_id

    @http.route(['/shop/customer_quote_submit'], type='json', methods=['POST'], auth="public", website=True)
    def customer_quote_submit(self, **kw):
        values = {
            'product_id': kw.get('product_id'),
            'qty': kw.get('qty'),
            'price': kw.get('price'),
            'description': kw.get('description'),
            'customer_id': request.env.user.partner_id.id,
            'website_currency_id': request.website.get_current_pricelist().currency_id.id,
        }
        quote_customer_email = request.env.user.partner_id.email
        if not quote_customer_email:
            request.env.user.partner_id.sudo().write({'email' : request.env.user.email})

        quote_obj = request.env['quote.quote'].sudo().create(values)
        values = {
            'new_price': kw.get('price'),
            'new_qty': kw.get('qty'),
            'new_desc': kw.get('description'),
            'quote_obj': quote_obj.sudo(),
        }
        temp_id = request.env['ir.ui.view']._render_template("website_quote_system.customer_quote_template_submit", values)
        return temp_id

    @http.route(['/quote/order/validate'], type='json', methods=['POST'], auth="public", website=True)
    def _get_quote_order_validate(self, **kw):
        so = request.website.sale_get_order()
        if so and so.website_order_line:
            invalid_lines = so.website_order_line.filtered(lambda l: l.customer_quote and request.env['quote.quote'].browse(l.ref_quote_id).status not in ['approved', 'incart'])
            if invalid_lines:
                return False
        return True

class OdooQuoteSystem(WebsiteSaleForm):

    @http.route(['/shop/quote/addtocart'], type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def quote_add_to_cart(self, **kw):
        quote_id = kw.get('quote_id') if kw.get('quote_id') else False
        quote_obj = request.env['quote.quote'].search([('id', '=', quote_id)])
        if not quote_obj.status == 'approved':
            return request.redirect(request.httprequest.referrer)

        add_qty = 1
        set_qty = 0
        product_id = int(kw.get('product_id')) if kw.get('product_id') else False
        product_price = kw.get('product_price') if kw.get('product_price') else False
        add_qty = kw.get('product_qty') if kw.get('product_qty') else False
        so = request.website.sale_get_order(force_create=1)
        # code to prevent issue of add_to_cart again from back button
        if so and so.website_order_line:
            for line in so.website_order_line:
                if line.product_id.id == product_id:
                    if line.ref_quote_id == int(quote_id):
                        return request.redirect('/shop/cart')

        so_id = so.with_context(quote_id=quote_id, quote_price=product_price)._cart_update(
            product_id=int(product_id),
            add_qty=float(add_qty) if add_qty else 1,
            set_qty=float(set_qty),
            quote_line=True, quote_id=quote_id, quote_price=product_price,
        )
        if not so_id.get("warning"):
            line_id = so_id.get('line_id') or False
            obj = request.env['sale.order.line'].sudo().browse([line_id])
            if obj and obj.exists():
                obj.price_unit = product_price
                obj.customer_quote = True
                obj.ref_quote_id = int(quote_id)
                obj.discount = 0
                if quote_id:
                    quote_id_obj = request.env['quote.quote'].browse([int(quote_id)])
                    quote_id_obj.status = 'incart'
                    quote_id_obj.send_quote_status_update_mail()
                    quote_id_obj.sale_order_id = obj.order_id.id
                    quote_id_obj.sale_order_line_id = line_id
        return request.redirect('/shop/cart')

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        res = super(WebsiteSale, self).payment_confirmation(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        order_obj = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        if order_obj:
            for line in order_obj.order_line:
                if line.customer_quote:
                    if line.ref_quote_id:
                        quote_obj = request.env['quote.quote'].search([('id', '=', line.ref_quote_id)])
                        if quote_obj.status == 'incart':
                            quote_obj.status = 'inprocess'
                            quote_obj.send_quote_status_update_mail()
        return res

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        res = super(WebsiteSale, self).payment(**post)
        order_id = request.website.sale_get_order()
        if not request.env.user == request.website.user_id:
            for order_line in order_id.order_line:
                if order_line.customer_quote:
                    quote_obj = request.env['quote.quote'].search([
                        ('sale_order_line_id', '=', order_line.id)
                    ])
                    if quote_obj:
                        from_currency = quote_obj.website_currency_id
                        order_line.price_unit = from_currency.compute(quote_obj.price, request.website.pricelist_id.currency_id)
                        order_line.discount = 0
        return res

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        if not request.env.user == request.website.user_id:
            quote_ids = request.env['quote.quote'].search([('sale_order_line_id', '=', line_id)])
            line_obj = request.env['sale.order.line'].sudo().browse(line_id)
            if quote_ids:
                for quote_id in quote_ids:
                    if line_obj.ref_quote_id:
                        set_qty = quote_id.qty if set_qty != 0 else 0
                        quote_id.status = 'approved' if set_qty == 0 else quote_id.status
        res = super(WebsiteSale, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)
        return res

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        so = request.website.sale_get_order()
        if so and so.website_order_line:
            invalid_lines = so.website_order_line.filtered(lambda l: l.customer_quote and request.env['quote.quote'].browse(l.ref_quote_id).status not in ['approved', 'incart'])
            if invalid_lines:
                return request.redirect("/shop/cart")
        res = super(WebsiteSale, self).checkout(**post)
        return res
