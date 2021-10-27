# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID

def _auto_create_category_if_not_exist(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    categ_obj = env['product.category']
    category_names = ["All / Saleable / MAV Solar array", "All / Saleable / Inverters", "All / Saleable / Modules", "All / Saleable / Wingman"]
    categ_fields = categ_obj._fields.keys()
    default_categ_data = categ_obj.default_get(categ_fields)
    
    for categ_name in category_names:
        categ_exist = categ_obj.search([('complete_name', 'ilike', categ_name)], limit=1)
        if not categ_exist:
            split_categs = categ_name.split(' / ')
            parent_id = False
            for ct in split_categs:
                categ_exist = categ_obj.search([('name', '=', ct), ('parent_id','=',parent_id)], limit=1)
                if not categ_exist:
                    vals = {}
                    vals.update(default_categ_data)
                    vals.update({'name':ct, 'parent_id': parent_id})
                    categ_exist = categ_obj.create(vals)
                parent_id = categ_exist.id 
