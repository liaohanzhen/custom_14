# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo import tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def hide_mp_menus_to_user(self, menu_data):
        """ Return the ids of the menu items hide to the user. """
        res = super(IrUiMenu, self).hide_mp_menus_to_user(menu_data=menu_data)
        pending_seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_draft_seller_group')[1]
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if pending_seller_group in groups_ids and officer_group not in groups_ids:
            core_sales_menu_id = self.env.ref('sale.sale_menu_root').id
            if core_sales_menu_id in menu_data:
                menu_data.remove(core_sales_menu_id)
        return res
