from odoo import fields, models, api
from odoo.exceptions import ValidationError


class BookCategory(models.Model):
    _name = 'book.category'

    name = fields.Char(string='Name')
    parent_id = fields.Many2one('book.category', string='Parent')
    child_ids = fields.One2many('book.category', 'parent_id', string='Child')

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError("Error!!, Recursion")
