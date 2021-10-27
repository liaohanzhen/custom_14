from odoo import fields,models


class StockPicking(models.Model):
    _inherit='stock.picking'
    
    date_confirmed = fields.Datetime('Confirmation Date', readonly=True)
    
    def action_confirm(self):
        self.write({'date_confirmed': fields.Datetime.now()})
        return super(StockPicking, self).action_confirm()