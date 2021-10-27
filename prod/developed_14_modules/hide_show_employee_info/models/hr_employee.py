# -*- coding: utf-8 -*-
from odoo import models, api
from lxml import etree

import json

class Employee(models.Model):
    _inherit = "hr.employee"
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Employee, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ('form'):
            if not self.user_has_groups('hide_show_employee_info.group_show_all_employee_information'):
                doc = etree.XML(res['arch'])
                if view_type in ('form'):
                    for node in doc.xpath('//notebook/page'):
                        if node.get('name') == 'public':
                            continue
#                         node.set('invisible', "1")
#                         node.set('attrs', '{}')
                        
                        node.set('modifiers', json.dumps({'invisible': True}))
                res["arch"] = etree.tostring(doc)
        return res
    