from odoo import fields, models, api


class Users(models.Model):
    _inherit = "res.users"

    active_for_chat = fields.Boolean(string="Active For Chat", default=False)

    @api.model
    def toggle_active_for_chat(self, uid, change, *args, **kwargs):
        User = self.env['res.users']
        user = User.browse(uid)
        if self.env.uid == uid and change:
            user.active_for_chat = not user.active_for_chat
        return user.active_for_chat
