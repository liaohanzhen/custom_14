# -*- coding: utf-8 -*-

from odoo.addons.project.controllers.portal import CustomerPortal
from odoo.http import request
#from odoo.addons.portal_documents.controllers.main import AttachmentCustomerPortal

# class AttachmentCustomerPortalProject(AttachmentCustomerPortal):
#     
#     def get_portal_documents_domain(self):
#         domain = super(AttachmentCustomerPortalProject, self).get_portal_documents_domain()
#         projects = request.env['project.project'].sudo().search(['|', ('partner_id','=',False),('partner_id','!=',request.env.user.partner_id.id)])
#         portal_attachment_ids = projects.mapped('portal_attachment_ids').ids
#         domain = [('id','not in',portal_attachment_ids)]+domain
#         return domain
    
class CustomerPortalProject(CustomerPortal):
    def _project_get_page_view_values(self, project, access_token, **kwargs):
        res = super(CustomerPortalProject, self)._project_get_page_view_values(project, access_token, **kwargs)
        res['task_count'] = request.env['project.project'].browse(project.id).task_count
        return res

#     def _prepare_portal_layout_values(self):
#         values = super(CustomerPortal, self)._prepare_portal_layout_values()
#         Project = request.env['project.project']
#         Task = request.env['project.task']
#         # portal users can't view projects they don't follow
#         
#         user = request.env.user
#         domain = ['|',('allowed_user_ids','in', [user.id]), ('allowed_group_ids','in',user.groups_id.ids)]
#         
#         portal_tasks = Task.sudo().search(domain)
#         portal_projects = portal_tasks.mapped('project_id')
#         
#         projects = Project.sudo().search([('partner_id','=',request.env.user.partner_id.id)])
#         total_tasks = len(portal_tasks+projects.mapped('tasks'))
#         total_projects = len(projects+portal_projects)
#         
#         values['project_count'] = total_projects #Project.search_count([('id', 'in', projects.ids)])
#         values['task_count'] = total_tasks #Task.search_count([('project_id', 'in', projects.ids)])
#         return values
    
    