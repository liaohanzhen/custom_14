from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute


class WebsiteSaleExt(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, brand=None, search_in_description=True):
        rtn = super(WebsiteSaleExt, self)._get_search_domain(search, category, attrib_values,
                                                             search_in_description=True)
        # brand = kwargs.get('brand')
        if brand:
            rtn.insert(0, '&')
            rtn.append(('product_brand_ept_id', '=', int(brand)))
        return rtn

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/brand/<model("product.brand.ept"):brand>''',
        '''/shop/brand/<model("product.public.brand"):brand>/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, brand=None, **post):
        rtn = super(WebsiteSaleExt, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        context = rtn.qcontext
        Brand = request.env['product.brand.ept']
        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/shop', brand=Brand, search=search, attrib=attrib_list, order=post.get('order'))
        if brand:
            brand = Brand.search([('id', '=', int(brand))], limit=1)
            if not brand or not brand.can_access_from_current_website():
                raise NotFound()

            if ppg:
                try:
                    ppg = int(ppg)
                    post['ppg'] = ppg
                except ValueError:
                    ppg = False
            if not ppg:
                ppg = request.env['website'].get_current_website().shop_ppg or 20

            ppr = request.env['website'].get_current_website().shop_ppr or 4

            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values, brand=brand)
            keep = QueryURL('/shop', brand=Brand, search=search, attrib=attrib_list, order=post.get('order'))
            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list

            Product = request.env['product.template'].with_context(bin_size=True)
            search_product = Product.search(domain, order=self._get_search_order(post))

            if brand:
                url = "/shop/brand/%s" % slug(brand)

            product_count = len(search_product)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            offset = pager['offset']
            products = search_product[offset: offset + ppg]

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            brands = Brand.search([])
            context.update({
                'brands': brands,
                'brand': brand,
                'search': search,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'products': products,
                'search_count': product_count,  # common for all searchbox
                'ppg': ppg,
                'ppr': ppr,
                'attributes': attributes,
                'keep': keep,
                # 'pricelist': pricelist,
                'bins': TableCompute().process(products, ppg, ppr),
                # 'search_categories_ids': search_categories.ids,
            })
        else:
            brands = Brand.search([])
            brand = Brand
            context.update({
                'brands': brands,
                'brand': brand,
                'keep': keep,
            })
        return rtn
