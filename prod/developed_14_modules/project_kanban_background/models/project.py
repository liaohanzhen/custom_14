# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
import re

class ProjectProject(models.Model):
    _inherit = 'project.project'
        
    project_type_id = fields.Many2one("project.project.type", string="Project Type") 
    image = fields.Binary("Image", related="project_type_id.image", attachment=True, store=True)
    
    _sql_constraints = [
        ('project_project_code_uniq', 'unique(project_code)', 'Project code already exists!'),
    ]
            
    @api.model
    def create(self, vals):
        if vals.get('project_type_id'):
            sequence = self.env['project.project.type'].browse(vals.get('project_type_id')).sequence_id
            if sequence:
                vals['project_code'] = sequence.next_by_id()
        return super(ProjectProject, self).create(vals)
    
    
    def name_get(self):
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_project_code', True) and d.get('project_code', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        result = []
        for project in self.sudo():
            mydict = {
                      'id': project.id,
                      'name': project.name,
                      'project_code': project.project_code,
                      }
            result.append(_name_get(mydict))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            projects = self.env['project.project']
            if operator in positive_operators:
                projects = self.search([('project_code', '=', name)] + args, limit=limit)
                
            if not projects and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching projects, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                projects = self.search(args + [('project_code', operator, name)], limit=limit)
                if not limit or len(projects) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(projects)) if limit else False
                    projects += self.search(args + [('name', operator, name), ('id', 'not in', projects.ids)], limit=limit2)
            elif not projects and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('project_code', operator, name), ('name', operator, name)],
                    ['&', ('project_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                projects = self.search(domain, limit=limit)
            if not projects and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    projects = self.search([('project_code', '=', res.group(2))] + args, limit=limit)
        else:
            projects = self.search(args, limit=limit)
        return projects.name_get()
    