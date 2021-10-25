from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_id = fields.Many2one('project.project', string='Project')

    def _prepare_invoice(self):
        self.ensure_one()
        rtn = super(SaleOrder, self)._prepare_invoice()
        if self.project_id:
            rtn.update({'project_id': self.project_id.id})
        return rtn


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        rtn = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        if order.project_id:
            rtn.update({'project_id': order.project_id.id})
        return rtn


class AccountMove(models.Model):
    _inherit = "account.move"

    project_id = fields.Many2one('project.project', string='Project', readonly=True)


class Picking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', string='Project', readonly=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        project_id = self.sale_line_id.order_id.project_id
        rtn = super(StockMove, self)._get_new_picking_values()
        if project_id:
            rtn.update({'project_id': project_id.id})
        return rtn


class Project(models.Model):
    _inherit = "project.project"

    order_ids = fields.One2many('sale.order', 'project_id', string='Order Ids')
    invoice_ids = fields.One2many('account.move', 'project_id', string='Invoice Ids')
    picking_ids = fields.One2many('stock.picking', 'project_id', string='Picking Ids')

    project_code = fields.Char(string='Project Code')

    sale_order_count = fields.Integer(string='Order Count', compute='_compute_count')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_count')
    picking_count = fields.Integer(string='Picking Count', compute='_compute_count')

    def _compute_count(self):
        self.sale_order_count = len(self.order_ids)
        self.invoice_count = len(self.invoice_ids)
        self.picking_count = len(self.picking_ids)

    def action(self, name, model):
        return {
            'name': _(name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': model,
            'domain': [('project_id', '=', self.id)],
        }

    def action_display_tree_form(self):
        caller = self.env.context.get('caller', False)
        return self.action(caller.replace('.', ' ').title(), caller) if caller else True
