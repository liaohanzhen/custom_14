# -*- coding: utf-8 -*-

import base64

from odoo import http, modules, tools
from odoo.http import request
from odoo.addons.website_sign.controllers.main import WebsiteSign
 
class WebsiteSignEXT(WebsiteSign):
    @http.route(['/sign/get_notes/<int:id>/<token>'], type='json', auth='public')
    def get_notes(self, id, token):
        request = http.request.env['signature.request'].sudo().search([('id', '=', id), ('access_token', '=', token)], limit=1)
        if not request:
            return []

        DateTimeConverter = http.request.env['ir.qweb.field.datetime']
        ResPartner = http.request.env['res.partner'].sudo()
        messages = request.message_ids.read(['message_type', 'author_id', 'date', 'body'])
        for m in messages:
            author_id = m['author_id'] and m['author_id'][0] or False
            author = ResPartner.browse(author_id)
            m['author_id'] = author and author.read(['name'])[0] or {}
            if author_id:
                m['author_id']['avatar'] = '/web/image/res.partner/%s/image_small' % author_id
            else:
                m['author_id']['avatar'] = '/website_sign_ext/user/avatar' 
                
            m['date'] = DateTimeConverter.value_to_html(m['date'], '')
        return messages
    
class WebsiteSignExtUser(http.Controller):
    
    @http.route(['/website_sign_ext/user/avatar'], type='http', auth="public",)
    def user_avatar(self, user_id=0, **post):
        #img_path = modules.get_module_resource('web', 'static/src/img', 'placeholder.png')
        img_path = modules.get_module_resource('base', 'static/src/img', 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()
        content = tools.image_resize_image_small(base64.b64encode(image))
        
        image_base64 = base64.b64decode(content)
        headers = [('Content-Type', 'image/png')]
        status = 200
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response