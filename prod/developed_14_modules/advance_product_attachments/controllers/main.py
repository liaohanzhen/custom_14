# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):

    @http.route(['/download/attachment'], type='json', auth="public", methods=['POST'], website=True)
    def download_attachment(self, pro_attachment_id):
        if pro_attachment_id:
            pro_attachment_id = int(pro_attachment_id)
            irAttachObj = request.env['product.attachment'].sudo().browse(pro_attachment_id)
            irAttachObj.downloads = irAttachObj.downloads + 1
        return True
