# coding: utf-8

from odoo import fields, models, api


class ProductSatCode(models.Model):
    _inherit = 'product.unspsc.code'

    deep_search = fields.Boolean(
        help='If this record is active, then the CFDI Importer will implement '
        'further logic to reach the correct product')
    product_count = fields.Integer(string='Product Count', copy=False,
        compute="_compute_product_count",  # store="True",
        help="The number of products under this SAT code (Does not consider children categories)")

    def _compute_product_count(self):
        sat_code_data = self.env['product.template'].read_group([('unspsc_code_id', 'in', self.ids)], ['unspsc_code_id'], ['unspsc_code_id'])
        mapped_data = dict((data['unspsc_code_id'][0], data['unspsc_code_id_count']) for data in sat_code_data)
        for category in self:
            category.product_count = mapped_data.get(category.id, 0)
