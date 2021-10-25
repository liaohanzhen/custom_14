from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    patient_id = fields.Many2one('hospital.patient', string="Patient")


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    patient_id = fields.Many2one('hospital.patient', string="Patient")

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.patient_id as patient_id"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.patient_id"

    # def _from(self):
    #     return super(PurchaseReport, self)._from() + " left join stock_picking_type spt on (spt.id=po.picking_type_id)"
