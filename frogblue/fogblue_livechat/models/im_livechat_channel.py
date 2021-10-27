from odoo import models


class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    def _get_available_users(self):
        """ get available user of a given channel
            :retuns : return the res.users having their im_status online
        """
        self.ensure_one()
        res = self.user_ids.filtered(lambda user: user.active_for_chat)
        return res
