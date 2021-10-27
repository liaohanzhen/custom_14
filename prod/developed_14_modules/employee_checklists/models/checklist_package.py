# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ChecklistItemsPackage(models.Model):
    _name = 'checklist.item.package'
    
    name = fields.Char("Name",required=1)
    emp_checklist_item_ids = fields.Many2many("hr.employee.checklists.item",'employee_checlist_item_package_rel','package_id','item_id',"Checklist Items")
