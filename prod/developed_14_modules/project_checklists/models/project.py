# -*- coding: utf-8 -*-
from odoo import models,fields,api
#from lxml import etree
#from odoo.osv.orm import setup_modifiers
from odoo.tools.safe_eval import safe_eval

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    checklist_progress = fields.Float(compute='_get_checklist_progress', store=True, string='Checklist Progress', group_operator="avg")
    base_field_ids     = fields.One2many('project.base.field.value', 'project_id', 'Project Fields')
    
    @api.depends('tasks.checklist_progress')
    def _get_checklist_progress(self):
        for project in self:
            #tasks = project.tasks.filtered(lambda x:x.checklist_items!=False)
            tasks = project.tasks.filtered(lambda x:x.checklist_items.ids!=[])
            if tasks:
                total_task_progress = sum(line.checklist_progress for line in tasks)
                project.checklist_progress = round(100.0 * (total_task_progress) / (len(tasks)*100), 2)
            else:
                project.checklist_progress = 0.0
    def create_project_custom_field(self):
        form = self.env.ref("project_checklists.view_model_fields_form_project_project",False)
        ctx = self._context.copy()
        project_model = self.env.ref('project.model_project_project',False)
        ctx.update({'default_is_project_custom_field':True, 'default_project_field_type':'char'})
        if project_model:
            ctx.update({'default_model_id':project_model.id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.model.fields',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'target': 'new',
            'context': ctx,
        }
        
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(ProjectProject, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type=='form':
#             eview = etree.fromstring(res['arch'])
#             placeholder = eview.xpath("//group[@name='placeholder_custom_project_fields']")
#             if len(placeholder):
#                 fields = self.env['ir.model.fields'].sudo().search([('is_project_custom_field','=', True),('model_id.model','=','project.project')])
#                 placeholder = placeholder[0]
#                 fields_get_data = self.fields_get()
#                 for field in fields:
#                     node = etree.Element('field', {'name': field.name,'colspan':"2"})
#                     placeholder.append(node)
#                     res['fields'].update({field.name:fields_get_data.get(field.name)})
#                     setup_modifiers(node, res['fields'][field.name])
#                 res['arch'] = etree.tostring(eview)
#         return res
                
class ProjectBaseField(models.Model):
    _name = 'project.base.field'
    
    name = fields.Char('Name', required=1)

class ProjectBaseFieldValue(models.Model):
    _name = 'project.base.field.value'
    
    attribute_id    = fields.Many2one('project.base.field', 'Field')
    value           = fields.Char('Value')
    project_id      = fields.Many2one('project.project', 'Project')
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        ctx = self._context.copy()
        if ctx.get('project_id'):
            args.append(('project_id','=',ctx.get('project_id')))
            
        elif ctx.get('task_id'):
            task = self.env['project.task'].sudo().browse(ctx.get('task_id'))
            args.append(('project_id','=',task.project_id.id))
            #self = self.filtered(lambda x: x.project_id.id==project.id)
        if ctx.get('added_related_fields'):
            args.append(('id','not in',safe_eval(ctx.get('added_related_fields'))))
            #self = self.filtered(lambda x:x.id not in safe_eval(ctx.get('added_related_fields')))
        return super(ProjectBaseFieldValue, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        
    def name_get(self):
#         ctx = self._context.copy()
        res = []
#         if ctx.get('project_id'):
#             self = self.filtered(lambda x: x.project_id.id==ctx.get('project_id'))
#         elif ctx.get('task_id'):
#             project = self.env['project.task'].sudo().browse(ctx.get('task_id'))
#             self = self.filtered(lambda x: x.project_id.id==project.id)
#         if ctx.get('added_related_fields'):
#             self = self.filtered(lambda x:x.id not in safe_eval(ctx.get('added_related_fields')))
                
        for record in self:
            res.append((record.id, record.attribute_id.name))
        return res
        
#         for record in self:
#             res.append((record.id, record.attribute_id.name+' : '+record.value))
        #return res
        