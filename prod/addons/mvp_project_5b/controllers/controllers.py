# -*- coding: utf-8 -*-
from odoo import http
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import UserError
import base64
import json
import requests

class MVPProject5B(http.Controller):
    
    @http.route(['/my/temporary/link'], auth='public', website=True)
    def temporary_routing_to_fix_smoke_and_mirror(self, **kw):
        sale_order_id = request.session.get('sale_last_order_id')
        return request.redirect('/my/orders/' + str(sale_order_id))
    
    @http.route(['/shop/cart/update2'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def update_order_cart(self, product_id, add_qty, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
            
        #_logger.error("Order object 2222222 [" + str(sale_order) + "][" + str(product_id) + "]")
        
        product_custom_attribute_values = None
        no_variant_attribute_values = None
        sale_order._cart_update(
            product_id=58,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        sale_order._cart_update(
            product_id=59,
            add_qty=1,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        #_logger.error("Order object 111111 [" + str(sale_order) + "][" + str(product_id) + "]")
        return request.redirect("/shop/cart")
        
    @http.route('/projectapi', auth='public', website=True)
    def projectapi(self, **kw):
        cta = 'projectapi'
        image = 'projectapi'
        application = ''
        projectId = ''
        return http.request.render('mvp_project_5b.page_project_api', {
            'root': '/',
            'application':application,
            'contents':'',
            'projectId':'',
            'project_image':'',
            'cta': cta,
            'image':image})
            
    @http.route('/projectapi/<string:projID>', auth='public', website=True)
    def projectapi_project(self, projID='', **kw):
        cta = 'projectapi'
        image = 'projectapi'
        application = ''
        projectId = projID
        project_image = ''
        p_name = ''
        p_count = ''
        p_power = ''
        if projID:
            #Old API
            #url = 'https://observer.getpylon.com/api/v1/projects/' + str(projID)
            #headers = {"Authorization" : "Bearer uO2Auo1K7RpxsJ82KupdNxPMeLRbH1ylmp6fSoLlLloRu8rs8vBh0neqDmfqUe"}
            
            url = 'https://app.getpylon.com/api/v1/projects/' + str(projID)
            headers = {"Authorization" : "Bearer Fcdl5Xi0tTMAL1tWIxSGUS4oqWDN08bXqLNbK7jxd5gunjCAJD1B5ftPLk5hGb8k"}
            
            #New API
            #url = 'https://api.getpylon.com/v1/solar_projects/' + str(projID)
            #headers = {"Authorization" : "Bearer uO2Auo1K7RpxsJ82KupdNxPMeLRbH1ylmp6fSoLlLloRu8rs8vBh0neqDmfqUe", "Accept" : "application/vnd.api+json"}
            
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                apival = res.status_code
            else:
                apival = json.dumps(res.json())
                apival = json.loads(apival)
                
                for vals in apival['designs']:
                    if vals['image']:
                        project_image = vals['image']
                        
                    for panels in vals['summary']['panel_groups']:
                        p_name = "MAV 5P5B" #panels['name']
                        p_id = 41 #panels['id']
                        p_count = panels['count']
                        p_power = panels['power']
                    
            _proj_data = {
                'project_id': str(apival['uid']),
                'name': str(apival['site_address']),
                'project_data': str(json.dumps(res.json())),
            }
            _create_obj = request.env['mvp.pylon.projects.5b']
            _create_id = _create_obj.sudo().create(_proj_data)
            
        else:
            apival = "Enter project ID in URL /projectapi/<projID>"
        
        return http.request.render('mvp_project_5b.page_project_api', {
            'root': '/',
            'application':application,
            #'contents':apival['data'], #New API
            'contents':apival, #Old API
            'projectId':projectId,
            'project_image':project_image,
            'p_name':p_name,
            'p_count':p_count,
            'p_power':p_power,
            'cta': cta,
            'image':image})