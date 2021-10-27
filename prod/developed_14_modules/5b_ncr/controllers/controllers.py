# -*- coding: utf-8 -*-
# from odoo import http


# class 5bNcr(http.Controller):
#     @http.route('/5b_ncr/5b_ncr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/5b_ncr/5b_ncr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('5b_ncr.listing', {
#             'root': '/5b_ncr/5b_ncr',
#             'objects': http.request.env['5b_ncr.5b_ncr'].search([]),
#         })

#     @http.route('/5b_ncr/5b_ncr/objects/<model("5b_ncr.5b_ncr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('5b_ncr.object', {
#             'object': obj
#         })
