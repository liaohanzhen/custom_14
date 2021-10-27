# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    portal_group_id = fields.Many2one('res.groups', domain=lambda self:[('category_id', '=', self.sudo().env.ref('base.module_category_user_type').id), ('id','not in', [self.sudo().env.ref('base.group_user').id, self.sudo().env.ref('base.group_public').id])], required=False, string='Portal',
        help="The portal that users can be added in or removed from.")
    
    def add_remove_portal_access(self, portal_group_id):
        #if portal_group_id:
        user_type_groups = self.env['res.groups'].sudo().search([('category_id', '=', self.sudo().env.ref('base.module_category_user_type').id)])
        user_type_group_ids = user_type_groups.ids
        for partner in self.with_context(active_test=False):
            user = partner.user_ids[0] if partner.user_ids else None
            # remove the user (if it exists) from the portal group
            if user:
                user_group_ids = user.groups_id.ids
                if portal_group_id in user_group_ids:
                    continue
                for ut_group_id in user_type_group_ids:
                    if ut_group_id in user_group_ids:
                        # if user belongs to portal only, deactivate it
                        if len(user.groups_id) <= 1:
                            user.write({'groups_id': [(3, ut_group_id)], 'active': False})
                        else:
                            user.write({'groups_id': [(3, ut_group_id)]})
                            
        portal_wiz = self.env['portal.wizard'].with_context(active_ids=self.ids).new({'portal_id': portal_group_id})
        portal_wiz.onchange_portal_id()
        val = portal_wiz._convert_to_write({name: portal_wiz[name] for name in portal_wiz._cache})
        for user in val.get('user_ids',[]):
            if len(user)==3 and user[0]==0 and user[1]==0:
                user[2].update({'in_portal': bool(portal_group_id)})
        try:
            wizard_rec = self.env['portal.wizard'].create(val)
            wizard_rec.action_apply()
        except Exception as e:
            raise Warning(str(e))
        return True
    
    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if 'portal_group_id' in vals:
            res.add_remove_portal_access(vals.get('portal_group_id'))
        #res = super(ResPartner, self).create(vals)
        
        return res
        
    def write(self, vals):
        if 'portal_group_id' in vals:
            self.add_remove_portal_access(vals.get('portal_group_id'))
        res = super(ResPartner, self).write(vals)
        
        return res