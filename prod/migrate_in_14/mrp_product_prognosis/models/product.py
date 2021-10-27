# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _name = "product.product"
    _inherit = "product.product"

#     @api.multi
    @api.depends('product_tmpl_id.bom_ids')
    def _compute_not_bom(self):
        """
        Compute method for not_bom (used to hide/unhide the mrp-computed fields)

        Attrs update:
         * not_bom - True if BoM is found, false otherwise

        Methods:
         * _bom_find - of mrp.bom to find available BoM
        """
        for product_id in self:
            bom_id = self.env["mrp.bom"]._bom_find(product=product_id)
            product_id.not_bom = False if bom_id else True

#     @api.multi
    def _compute_available_for_assembly(self):
        """
        Compute method for available_for_assembly, bottleneck_product, prognosis_for_assembly

        Methods:
         * _bom_find - of mrp.bom to find available BoM line required to produce this product
         * _find_bom_lines - of product.product to find lines requried to produce this product
        """
        for product_id in self:
            bom_id = self.env["mrp.bom"]._bom_find(product=product_id)
            if bom_id:
                bom_lines_ids = product_id._find_bom_lines(bom_id=bom_id)
                # For the case when there are 2 lines with the same product
                new_dict = {}
                for product in bom_lines_ids:
                    if product['product_id'] in new_dict.keys():
                        new_dict[product['product_id']]['product_qty'] += product['product_qty']
                    else:
                        new_dict[product['product_id']] = product
                new_values = new_dict.values()

                # Calculate real potential & bottleneck
                count_available = False
                for product in new_values:
                    product_type = self.browse(product["product_id"]).type
                    # Only stockable products are taken into account
                    if product_type == "product":
                        # In case zero or less stocks, no sense to continue.
                        # We use it as a bottleneck disregarding what is found the next
                        if product['product_qty_available'] <= 0:
                            product_id.available_for_assembly = 0
                            product_id.bottleneck_product = product['product_id']
                            break

                        # Check the previous found min with this product requried stocks
                        count_available_new = 0
                        try:
                            count_available_new = product['product_qty_available'] // product['product_qty']
                        except ZeroDivisionError:
                            _logger.critical("Zero division in compute for {0}".format(product_id))

                        if count_available > count_available_new or not count_available:
                            count_available = count_available_new
                            product_id.available_for_assembly = count_available
                            product_id.bottleneck_product = product['product_id']

                # Calculate virtual potential
                count_virtual_available = False
                for product in new_values:
                    product_type = self.browse(product["product_id"]).type
                    # Only stockable products are taken into account
                    if product_type == "product":
                        # In case zero or less stocks, no sense to continue.
                        if product['product_virtual_available'] <= 0:
                            product_id.prognosis_for_assembly = 0
                            break

                        count_available_new = 0
                        try:
                            count_virtual_available_new = product['product_virtual_available'] // product['product_qty']
                        except ZeroDivisionError:
                            _logger.critical("Zero division in compute for {0}".format(product_id))

                        # Check the previous found min with this product virtual stocks
                        if count_virtual_available > count_virtual_available_new or not count_virtual_available:
                            count_virtual_available = count_virtual_available_new
                            product_id.prognosis_for_assembly = count_virtual_available
            else:
                # No Bom No qaugers!
                product_id.available_for_assembly = 0
                product_id.prognosis_for_assembly = 0
                product_id.bottleneck_product = False

    not_bom = fields.Boolean(
        compute=_compute_not_bom,
        compute_sudo=True,
        store=True,
        string="No BOM",
    )
    available_for_assembly = fields.Float(
        compute=_compute_available_for_assembly,
        compute_sudo=True,
        store=False,
        string="MRP Potential",
        help="Theoretically possible number of end products based on bill of materials and stocks availability.",
    )
    bottleneck_product = fields.Many2one(
        'product.product',
        string='Bottleneck Component',
        compute=_compute_available_for_assembly,
        compute_sudo=True,
        store=False,
    )
    prognosis_for_assembly = fields.Float(
        compute=_compute_available_for_assembly,
        compute_sudo=True,
        store=False,
        string="MRP Potential forecast",
        help="Available for assembly + Predicted residues of components.",
    )

    def _find_bom_lines(self, bom_id):
        """
        Method helper to find bom lines required to produce this product

        Args:
         * bom_id - 'mrp.bom' object

        Return:
         * list of dicts
            ** product_name - char
            ** product ID - integer
            ** qty required by Bom - float
            ** real stocks - float
            ** virtual stocks - float

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        result = []
        for bom_line_id in bom_id.bom_line_ids:
            # Check whether this bom is suitable for this product (attributes should be the same)
            if bom_line_id.bom_product_template_attribute_value_ids:
                if (set(map(int, bom_line_id.bom_product_template_attribute_value_ids or [])) - set(map(int, self.bom_product_template_attribute_value_ids))):
                    continue
            product_id = bom_line_id.product_id
            self.invalidate_cache(ids=[product_id.id])
            # The last 2 lines have "+" to make calculations recursive: we take into account the parts of parts of parts
            result.append({
                'name': product_id.name,
                'product_id': product_id.id,
                'product_qty': bom_line_id.product_qty,
                'product_qty_available': product_id.qty_available + product_id.available_for_assembly,
                'product_virtual_available': product_id.virtual_available + product_id.prognosis_for_assembly,
            })

        _logger.debug(u"The following BoM lines have been found".format(result))
        return result
