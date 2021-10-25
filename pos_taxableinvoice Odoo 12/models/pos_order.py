from pprint import pprint as pp
from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_taxable_invoice(self, orders):
        invoice_ids = []
        for rec in orders:
            order = self.env['pos.order'].browse(rec)
            invoice_id = order.invoice_id.id
            invoice_ids.append(invoice_id)
            print(invoice_id)
        return invoice_ids
