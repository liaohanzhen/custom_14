import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class ServiceRequest(http.Controller):
    @http.route('/quick/get_translations', website=True, auth="public", csrf=False, type='json')
    def get_translations(self):
        languages = []
        if 'lang' in request.env.context:
            getLang = request.env['ir.translation'].sudo().search([('module', '=', 'rt_quick_order'), ('lang', '=', request.env.context['lang']),
                     ('state', '=', 'translated')])
            for lang in getLang:
                vals = {'src': lang.src, 'value': lang.value}
                languages.append(vals)

        return languages, request.env.context

    @http.route('/quick/order', website=True, auth="public", csrf=False)
    def service_request(self):
        return http.request.render("rt_quick_order.quick_order_form", {})

    @http.route('/quick/get_products_variants', website=True, auth="public", csrf=False, type='json')
    def get_products_variants(self, params):
        # refs = [{'1': 'PRoSW'}, {'2': 'aaa'}, {'3': 'PS'}] // Expected Input [{row_no, ref_no}]
        attribute_str = request.env['ir.config_parameter'].sudo().get_param('rt_quick_order.attribute_ids')
        attr_id = int(''.join(filter(lambda i: i.isdigit(), attribute_str)))
        data = []
        for ref in params:
            # Check if not any Variant of the Product
            request.env.cr.execute("""select product_tmpl_id as pro_id from  product_product 
                                        where product_tmpl_id in (select product_tmpl_id as id 
                                        from product_product where default_code ilike %s and combination_indices = '')""",
                                (list(ref.values())[0],))
            res = request.env.cr.dictfetchall()
            if not res:
                # Check the Settings selected Attribute exist in the product
                request.env.cr.execute("""select product_attribute_id as attr_id from product_attribute_product_template_rel 
                                            where product_attribute_id = %s and product_template_id = 
                                            (select product_tmpl_id from product_product where default_code ilike %s)""",
                                    (attr_id, list(ref.values())[0],))
                res = request.env.cr.dictfetchall()

                # Fetching data of product variants
                query = """select pt.id as pro_id, pt.name as pro_name, pav.id as att_id, pav.name as att_val, pa.id
                                    from product_template pt, product_product pp, product_attribute pa,
                                    product_attribute_product_template_rel pa_rel, product_attribute_value pav,
                                    product_template_attribute_value ptav, (select product_tmpl_id as id 
                                    from product_product where default_code ilike %s) ptemp_id
                                    where pt.id = pp.product_tmpl_id and pa_rel.product_attribute_id = pa.id
                                    and ptav.product_tmpl_id = pt.id and pav.id in (ptav.product_attribute_value_id)
                                    and pav.attribute_id = pa.id and pp.product_tmpl_id = ptemp_id.id"""
                params = [list(ref.values())[0]]

                # Append the query with the Product Attribute ID
                if res:
                    query += ' and pa.id = %s'
                    params.append(res[0]['attr_id'])
                else:
                    query += ' and pa.id = (select attribute_id from  product_template_attribute_value where ' \
                             'product_tmpl_id = ptemp_id.id limit 1)'

                query += ' group by pa.id, pro_id, att_id, pro_name, att_val'

                request.env.cr.execute(query, params)
                res = request.env.cr.dictfetchall()
            data.append({'row': list(ref.keys())[0],
                         'pro_id': res[0]['pro_id'] if res else False,
                         'pro_name': res[0]['pro_name'] if res and 'pro_name' in res[0] else False,
                         'variants': []
                         })
        return data

    @http.route('/quick/get_product_details', website=True, auth="public", csrf=False, type='json')
    def get_product_details(self, params):
        data = []
        currency_symbol = ""
        if request.env.ref('base.main_company').currency_id and request.env.ref('base.main_company').currency_id.symbol:
            currency_symbol = request.env.ref('base.main_company').currency_id.symbol

        for ref in params:
            if 'att_val' in ref:
                request.env.cr.execute("""select pp.id as pro_id, pp.combination_indices as comb_id
                            from product_product pp, product_template_attribute_value ptav, product_template pt,
                            (select ptav.id as comb_id from  product_template_attribute_value ptav
                            where ptav.product_tmpl_id = {0} and ptav.product_attribute_value_id = {1}) pro_comb
                            where ptav.product_tmpl_id = pp.product_tmpl_id and pp.product_tmpl_id = pt.id
                            and pp.product_tmpl_id = {0} and ptav.product_attribute_value_id = {1} order by pro_id limit 1;""" \
                                    .format(ref['pro_id'], ref['att_val']))
                res = request.env.cr.dictfetchall()
                if res:
                    product = request.env['product.product'].sudo().search([('id', '=', res[0]['pro_id'])], limit=1)
                else:
                    product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', ref['pro_id'])], limit=1)
            else:
                product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', ref['pro_id'])], limit=1)
            if product:
                attributes = ','.join(str(x) for x in product.product_template_attribute_value_ids.ids)
                pricelist_context, pl = WebsiteSale._get_pricelist_context(self)
                p = request.env['product.product'].with_context(pricelist_context, display_default_code=False).browse(
                    product.id)
                price = p._get_combination_info_variant()['price']

                partner_obj = request.env['res.users'].sudo().browse(request.session.uid).partner_id
                #tax_price = product.taxes_id.sudo().compute_all(product.lst_price, quantity=1, product=product, partner=partner_obj)['total_included']
                data.append({'row': ref['row_id'],
                             'pro_id': product.id,
                             'pro_name': product.product_tmpl_id.name,
                             'pro_desc': product.description_sale or '',
                             'tax_price': price or 0,
                             'untax_price': product.lst_price or 0,
                             'delivery': product.sale_delay if product.sale_delay > 0 else 1,
                             'attributes': '',
                             'currency_symbol': currency_symbol,
                             })
        return data

    @http.route(['/bulk_products'], auth="public", website=True, csrf=False)
    def add_bulk_to_cart(self, **kw):
        for pro in json.loads(kw['cart_products']):
             request.website.sale_get_order(force_create=1)._cart_update(product_id=int(pro['pro_id']), add_qty=float(pro['qty']))

        return request.redirect('/shop/cart')

    @http.route('/quick/get_product_reference', website=True, auth="public", csrf=False, type='json')
    def get_product_reference(self, params):
        products = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(params))])
        for pro in products:
            if pro.default_code:
                return pro.default_code
        return False
