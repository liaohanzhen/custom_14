from odoo import models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    def message_update(self, msg, update_vals=None):
        if update_vals is None:
            update_vals = {}
        if len(self.ids)==1:
            company = self.company_id
            if company.auto_move_tickets_to_new_stage and self.stage_id.id in company.stagechange_source_stage.ids and company.stagechange_destination_stage:
                update_vals.update({'stage_id' : company.stagechange_destination_stage.id})
            
            return super(HelpdeskTicket, self).message_update(msg, update_vals=update_vals)
        else:
            for ticket in self:
                company = ticket.company_id
                if company.auto_move_tickets_to_new_stage and ticket.stage_id.id in company.stagechange_source_stage.ids and company.stagechange_destination_stage:
                    ticket.write({'stage_id' : company.stagechange_destination_stage.id})
                
            return super(HelpdeskTicket, self).message_update(msg, update_vals=update_vals)