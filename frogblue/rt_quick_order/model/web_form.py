from odoo import models, fields
from odoo.http import request


class QuickOrder(models.Model):
    _name = "quick.order"
    _inherit = ['website.menu']

    def get_products_variants(self, refs):
        # refs = [{'1': 'PRoSW'}, {'2': 'aaa'}, {'3': 'PS'}] // Expected Input [{row_no, ref_no}]
        attribute_str = self.env['ir.config_parameter'].sudo().get_param('rt_quick_order.attribute_ids')
        attr_id = int(''.join(filter(lambda i: i.isdigit(), attribute_str)))
        data = []
        for ref in refs:
            # Check if not any Variant of the Product
            self.env.cr.execute("""select product_tmpl_id as pro_id from  product_product 
                                where product_tmpl_id in (select product_tmpl_id as id 
                                from product_product where default_code ilike %s and combination_indices = '')""",
                                (list(ref.values())[0],))
            res = self.env.cr.dictfetchall()
            if not res:
                # Check the Settings selected Attribute exist in the product
                self.env.cr.execute("""select product_attribute_id as attr_id from product_attribute_product_template_rel 
                                    where product_attribute_id = %s and product_template_id = 
                                    (select product_tmpl_id from product_product where default_code ilike %s)""",
                                    (attr_id, list(ref.values())[0],))
                res = self.env.cr.dictfetchall()

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

                self.env.cr.execute(query, params)
                res = self.env.cr.dictfetchall()
            data.append({'row': list(ref.keys())[0],
                         'pro_id': res[0]['pro_id'] if res else False,
                         'pro_name': res[0]['pro_name'] if res and 'pro_name' in res[0] else False,
                         'variants': [{r['att_id']:r['att_val']} for r in res] if res and 'att_id' in res[0] else []
                         })
        return data

    def get_product_details(self, refs):
        # refs = [{row_id: "1", att_val: "8", pro_id: "31"}] // Expected Input
        data = []
        currency_symbol = ""
        if self.env.ref('base.main_company').currency_id and self.env.ref('base.main_company').currency_id.symbol:
            currency_symbol = self.env.ref('base.main_company').currency_id.symbol

        for ref in refs:
            if 'att_val' in ref:
                self.env.cr.execute("""select pp.id as pro_id, pp.combination_indices as comb_id
                    from product_product pp, product_template_attribute_value ptav, product_template pt,
                    (select ptav.id as comb_id from  product_template_attribute_value ptav
                    where ptav.product_tmpl_id = {0} and ptav.product_attribute_value_id = {1}) pro_comb
                    where ptav.product_tmpl_id = pp.product_tmpl_id and pp.product_tmpl_id = pt.id
                    and pp.product_tmpl_id = {0} and ptav.product_attribute_value_id = {1}
                    and pp.combination_indices like CONCAT(pro_comb.comb_id, ',%') or pp.combination_indices like CONCAT('%,', pro_comb.comb_id)
                    or pp.combination_indices like cast(pro_comb.comb_id as varchar(100)) order by pro_id limit 1;""" \
                    .format(ref['pro_id'], ref['att_val']))
                res = self.env.cr.dictfetchall()
                if res:
                    product = self.env['product.product'].search([('id', '=', res[0]['pro_id'])])
            else:
                product = self.env['product.product'].search([('product_tmpl_id', '=', ref['pro_id'])])

            if product:
                attributes = ','.join(str(x) for x in product.product_template_attribute_value_ids.ids)
                partner_obj = self.env['res.users'].browse(request.session.uid).partner_id
                tax_price = product.taxes_id.compute_all(product.lst_price, quantity=1, product=product, partner=partner_obj)['total_included']
                data.append({'row': ref['row_id'],
                             'pro_id': product.id,
                             'pro_name': product.product_tmpl_id.name,
                             'pro_desc': product.description or '',
                             'tax_price': product.lst_price, #tax_price or 0,
                             #'untax_price': product.lst_price or 0,
                             'delivery': product.sale_delay if product.sale_delay > 0 else 1,
                             'attributes': attributes if attributes else '',
                             'currency_symbol': currency_symbol,
                             })
        return data