from odoo import models


class SaleOrderLine(models.Model):
    _inherit='sale.order.line'
    
    
    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        ctx = self._context or {}
        skip_partner_context = False
        if ctx.get('website_id') and ctx.get('lang'):
            skip_partner_context=True
        for ptav in (no_variant_ptavs - custom_ptavs):
            if skip_partner_context:
                name += "\n" + ptav.display_name
            else:
                name += "\n" + ptav.with_context(lang=self.order_id.partner_id.lang).display_name

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        custom_values = sorted(self.product_custom_attribute_value_ids, key=lambda r: (r.custom_product_template_attribute_value_id.id, r.id))
        # display the is_custom values
        for pacv in custom_values:
            if skip_partner_context:
                name += "\n" + pacv.display_name
            else:
                name += "\n" + pacv.with_context(lang=self.order_id.partner_id.lang).display_name
        return name
