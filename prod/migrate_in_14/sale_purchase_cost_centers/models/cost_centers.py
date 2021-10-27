# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import ast

class CostCenters(models.Model):
    """docstring for CostCenters"""
    _name = 'cost.centers'
    _description = 'Costcenter Code'
    _rec_name = 'code'
    
    code = fields.Char(string='Code' ,required=True)
    title = fields.Char(string='Title' ,required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

#     @api.multi
    def name_get(self):
        res = []
        for order in self:
            name = str(order.code) +" "+ str(order.title)
            res.append((order.id, name))
        return res

class SaleOrder(models.Model):
    """docstring for SaleOrder"""
    _inherit = 'sale.order'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

#     @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if res:
            res.update({'cost_centers_id': self.cost_centers_id and self.cost_centers_id.id})
        return res

#     @api.multi
    @api.onchange('cost_centers_id')
    def onchange_cost_centers_id(self):
        for order in self:
            if order.order_line:
                order.order_line.update({'cost_centers_id': order.cost_centers_id and order.cost_centers_id.id})

class SaleOrderLine(models.Model):
    """docstring for SaleOrderLine"""
    _inherit = 'sale.order.line'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

#     @api.multi
    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if res:
            res.update({'cost_centers_id': self.cost_centers_id and self.cost_centers_id.id})
        return res

class PurchaseOrder(models.Model):
    """docstring for PurchaseOrder"""
    _inherit = 'purchase.order'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center' )

#     @api.multi
    def action_view_invoice(self, invoices=False):
        res = super(PurchaseOrder, self).action_view_invoice(invoices=invoices)
        if res:
            ctx = ast.literal_eval(res['context'])
            ctx.update({'default_cost_centers_id': self.cost_centers_id and self.cost_centers_id.id})
#             res['context'].update({'default_cost_centers_id': self.cost_centers_id and self.cost_centers_id.id})
            res['context'] = str(ctx)
        return res

#     @api.multi
    @api.onchange('cost_centers_id')
    def onchange_cost_centers_id(self):
        for order in self:
            if order.order_line:
                order.order_line.update({'cost_centers_id': order.cost_centers_id and order.cost_centers_id.id})

class PurchaseOrderLine(models.Model):
    """docstring for PurchaseOrderLine"""
    _inherit = 'purchase.order.line'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center' )

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        if res:
            line_id = self.env['purchase.order.line'].browse(res['purchase_line_id'])
            res.update({'cost_centers_id': line_id.cost_centers_id and line_id.cost_centers_id.id})
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

#     def _prepare_purchase_order(self, product_id, product_qty, product_uom, origin, values, partner):
    def _prepare_purchase_order(self, company_id, origins, values):
#         res = super(StockRule, self)._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        if res:
            order_id = self.env['sale.order'].search([('name','like', res['origins'])], limit=1)
            if order_id:
                res.update({'cost_centers_id': order_id.cost_centers_id and order_id.cost_centers_id.id})
        return res

#     def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, values, po, partner):
    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
#         res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, partner)
        res = super(StockRule, self)._update_purchase_order_line(product_id, product_qty, product_uom, company_id, values, line)
        if res:
            order_id = self.env['purchase.order'].browse(res['order_id'])
            if order_id:
                res.update({'cost_centers_id': order_id.cost_centers_id and order_id.cost_centers_id.id})
        return res

class AccountInvoice(models.Model):
    """docstring for AccountInvoice"""
    _inherit = 'account.move'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

#     def _prepare_invoice_line_from_po_line(self, line):
#         res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line=line)
#         if res:
#             line_id = self.env['purchase.order.line'].browse(res['purchase_line_id'])
#             res.update({'cost_centers_id': line_id.cost_centers_id and line_id.cost_centers_id.id})
#         return res

#     @api.multi
    @api.onchange('cost_centers_id')
    def onchange_cost_centers_id(self):
        for order in self:
            if order.invoice_line_ids:
                order.invoice_line_ids.update({'cost_centers_id': order.cost_centers_id and order.cost_centers_id.id})

class AccountInvoiceLine(models.Model):
    """docstring for AccountInvoiceLine"""
    _inherit = 'account.move.line'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

class HREmployee(models.Model):
    """docstring for HREmployee"""
    _inherit = 'hr.employee'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

class HRExpense(models.Model):
    """docstring for HRExpense"""
    _inherit = 'hr.expense'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

    @api.onchange('employee_id')
    def _onchange_cost_centers_id(self):
        if self.employee_id:
            self.cost_centers_id = self.employee_id.cost_centers_id and self.employee_id.cost_centers_id.id

#     @api.multi
    def action_submit_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        cost_centers_id = False
        if self.cost_centers_id:
            cost_centers_id = self.cost_centers_id and self.cost_centers_id.id
        return {
            'name': _('New Expense Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_employee_id': self[0].employee_id.id,
                'default_name': todo[0].name if len(todo) == 1 else '',
                'default_cost_centers_id': cost_centers_id,
            }
        }

class HRExpenseSheet(models.Model):
    """docstring for HRExpenseSheet"""
    _inherit = 'hr.expense.sheet'

    cost_centers_id = fields.Many2one('cost.centers' ,string='Cost Center')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: