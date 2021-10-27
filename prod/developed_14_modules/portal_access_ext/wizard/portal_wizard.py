# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import api, fields, models


class PortalWizard(models.TransientModel):
    _inherit = 'portal.wizard'
    
    def _default_portal(self):
        return self.env.ref('base.group_portal')
    
    def _default_user_ids(self):
        return
    
    portal_id = fields.Many2one('res.groups', domain=lambda self:[('category_id', '=', self.sudo().env.ref('base.module_category_user_type').id), ('id','not in', [self.sudo().env.ref('base.group_user').id, self.sudo().env.ref('base.group_public').id])], required=False, string='Portal',
        default=_default_portal, help="The portal that users can be added in or removed from.")
    
#     def _default_user_ids(self):
#         # for each partner, determine corresponding portal.wizard.user records
#         partner_ids = self.env.context.get('active_ids', [])
#         contact_ids = set()
#         user_changes = []
#         for partner in self.env['res.partner'].sudo().browse(partner_ids):
#             contact_partners = partner.child_ids | partner
#             for contact in contact_partners:
#                 # make sure that each contact appears at most once in the list
#                 if contact.id not in contact_ids:
#                     contact_ids.add(contact.id)
#                     in_portal = False
#                     if contact.user_ids:
#                         in_portal = self.env.ref('base.group_portal') in contact.user_ids[0].groups_id
#                     user_changes.append((0, 0, {
#                         'partner_id': contact.id,
#                         'email': contact.email,
#                         'in_portal': in_portal,
#                     }))
#         return user_changes
    
    @api.onchange('portal_id')
    def onchange_portal_id(self):
        # for each partner, determine corresponding portal.wizard.user records
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        if self.user_ids:
            for user in self.user_ids:
                user_changes.append((2,user.id))
         
        user_type_categ_id = self.sudo().env.ref('base.module_category_user_type').id        
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids | partner
            for contact in contact_partners:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal = False
                    assigned_portal_group_id = None
                    if contact.user_ids:
                        user_groups = contact.user_ids[0].groups_id
                        in_portal = self.portal_id in user_groups
                        assigned_group = user_groups.filtered(lambda x:x.category_id.id==user_type_categ_id)
                        assigned_portal_group_id = assigned_group and assigned_group[0].id
                         
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                        'portal_group_id' : assigned_portal_group_id,
                    }))
        self.user_ids = user_changes


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'
    
    portal_group_id = fields.Many2one('res.groups', string='Assigned Group', help="The portal group in that users are currently belong.")
    
    #domain=lambda self:[('category_id', '=', self.sudo().env.ref('base.module_category_user_type').id), ('id','not in', [self.sudo().env.ref('base.group_user').id, self.sudo().env.ref('base.group_public').id])], 
    
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """ From selected partners, add corresponding users to chosen portal group. It either granted
            existing user, or create new one (and add it to the group).
        """
        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        for wizard_user in self.sudo().with_context(active_test=False):
            group_portal = wizard_user.wizard_id.portal_id or self.env.ref('base.group_portal')
            #group_portal = self.env.ref('base.group_portal')
            #Checking if the partner has a linked user
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            # add portal group to relative user of selected partners
            if wizard_user.in_portal:
                user_portal = None
                # create a user if necessary, and make sure it is in the portal group
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env['res.company']._company_default_get('res.users').id
                    user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
                else:
                    user_portal = user
                wizard_user.write({'user_id': user_portal.id})
                if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                    # prepare for the signup process
                    wizard_user.user_id.partner_id.signup_prepare()
                wizard_user.with_context(active_test=True)._send_email()
                wizard_user.refresh()
            else:
                # remove the user (if it exists) from the portal group
                if user and group_portal in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})

