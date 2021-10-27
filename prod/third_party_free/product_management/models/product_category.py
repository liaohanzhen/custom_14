#coding: utf-8

from odoo import api, models


class product_category(models.Model):
    """
    Re-write to implement methods needed by js interface
    """
    _inherit = "product.category"

    @api.model
    def return_categories_hierarchy(self):
        """
        The method to return categories in jstree format

        Methods:
         * _return_categories_recursive

        Returns:
         * list of folders dict with keys:
           ** id
           ** text - folder_name
           ** icon
           ** children - array with the same keys
        """
        self = self.with_context(lang=self.env.user.lang)
        categories = self.search([("parent_id", "=", False)])
        res = []
        for category in categories:
            res.append(category._return_categories_recursive())
        return res

    def _return_categories_recursive(self):
        """
        The method to go by all categories recursively to prepare their list in js_tree format

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        res = {
            "text": self.name,
            "id": self.id,
        }
        child_res = []
        child_ids = self.search([("id", "in", self.child_id.ids)])
        for child in child_ids:
            child_res.append(child._return_categories_recursive())
        res.update({"children": child_res})
        return res
