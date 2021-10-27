# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HelpdeskTicket(models.Model):
    """Extend with number field and generate it via sequence on create."""

    _inherit = 'helpdesk.ticket'

    name_no = fields.Char('No.', readonly=True)

    @api.model
    def create(self, vals):
        """Generate and return sequence number for ticket."""
        name_no = self.env['ir.sequence'].next_by_code('helpdesk.ticket.no')
        if name_no:
            vals['name_no'] = name_no
        return super(HelpdeskTicket, self).create(vals)

    @api.depends('name', 'name_no')
    def name_get(self):
        """Extend to include sequence number in name."""
        res = []
        for rec in self:
            if rec.name_no:
                res.append((rec.id, "[%s] %s" % (rec.name_no, rec.name)))
            else:
                res.append((rec.id, "%s" % rec.name))
        return res
    
    def message_post_with_template(self, template_id, **kwargs):
        if template_id:
            ctx = self._context.copy()
            ctx.update({'mail_notify_force_send':False})
            return super(HelpdeskTicket, self.with_context(ctx)).message_post_with_template(template_id, **kwargs)
        return super(HelpdeskTicket, self).message_post_with_template(template_id, **kwargs)
    
    def assign_ticket_to_self_and_open(self):
        self.ensure_one()
        #self.user_id = self.env.user
        stage_ids = self.team_id.stage_ids.ids
        vals = {'user_id':self.env.user.id}
        try:
            current_stage_index = stage_ids.index(self.stage_id.id)
            current_stage_index +=1
            if len(stage_ids)>current_stage_index:
                next_stage = self.team_id.stage_ids[current_stage_index]
                vals.update({'stage_id':next_stage.id})
        except Exception as e:
            pass
        self.write(vals)
        return True
        
        
    