# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import html2plaintext


class project_portfolio(http.Controller):
    @http.route([
        '/projects',
    ], type='http', auth="public", website=True)
    def portfolio(self, **post):
        project_obj = request.env["project.project"]
        portfolio_category_obj = request.env["portfolio.category"]
        
        search_categories = portfolio_category_obj.sudo().search([('is_active','=',True)])
        search_projects = project_obj.sudo().search([('is_publish','=',True)])

        return request.render("sh_project_portfolio.projects", {'projects':search_projects,'categories':search_categories})
   
    
    
    @http.route(['/project/<int:project>'], type='http', auth="public", website=True)
    def project_page(self,project, **post):
        """ Prepare all values to display the portfolio.
        """

        values = {
            'project': request.env["project.project"].sudo().search([('id','=',project)],limit=1)
        }
        return request.render("sh_project_portfolio.sh_project", values)  