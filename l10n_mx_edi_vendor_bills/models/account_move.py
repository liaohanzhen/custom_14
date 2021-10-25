# coding: utf-8

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"


    check_tax = fields.Monetary(
        string="Verification tax",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False)
    check_total = fields.Monetary(
        string="Verification total",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False)
    x_tax_difference = fields.Monetary(
        string="Tax difference", compute="_compute_tax_and_total_difference")
    x_total_difference = fields.Monetary(
        string="Total difference", compute="_compute_tax_and_total_difference")


    @api.depends("check_total", "amount_total")
    def _compute_tax_and_total_difference(self):
        for invoice in self:
            invoice.x_tax_difference = 0.0
            invoice.x_total_difference = 0.0
            if invoice.check_tax and invoice.check_total:
                invoice.x_tax_difference = float_round(
                    invoice.check_tax - invoice.amount_tax,
                    precision_rounding=invoice.currency_id.rounding)
                invoice.x_total_difference = float_round(
                    invoice.check_total - invoice.amount_total,
                    precision_rounding=invoice.currency_id.rounding)

    #Extend original method
    def action_post(self):
        for inv in self:
            if inv.check_tax or inv.check_total:
                if float_compare(inv.check_total, inv.amount_total, precision_rounding=inv.currency_id.rounding) != 0 or float_compare(inv.check_tax, inv.amount_tax, precision_rounding=inv.currency_id.rounding) != 0:
                    raise ValidationError(_(
                        "Verify the invoice total and taxes\n\n"
                        "Total amount: %s -->  Verification total amount: %s. Difference: %s\n"
                        "Tax amount: %s --> Verification tax amount: %s. Difference: %s\n") % (
                            formatLang(self.env, inv.amount_total),
                            formatLang(self.env, inv.check_total),
                            formatLang(self.env, inv.x_total_difference),
                            formatLang(self.env, inv.amount_tax),
                            formatLang(self.env, inv.check_tax),
                            formatLang(self.env, inv.x_tax_difference))
                    )
        return super().action_post()