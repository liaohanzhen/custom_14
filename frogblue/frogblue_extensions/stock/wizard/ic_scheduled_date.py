# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class InterCompanyScheduledDate(models.TransientModel):
    _name = 'ic.picking.date'
    _description = 'IC Picking Date'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    scheduled_date = fields.Datetime('Scheduled date', required=True)
    update_ic_pickings = fields.Boolean('Update on intercompany pickings?', default=True)

    def update_scheduled_date(self):
        self.ensure_one()
        self = self.sudo()

        picking = self.picking_id

        if not picking or not picking.is_intercompany:
            return False

        dropship_pick_type = self.env.ref('stock_dropshipping.picking_type_dropship', raise_if_not_found=False)
        ic_model, ic_ids = picking._get_intercompany_records()
        ic_records = self.env[ic_model].browse(ic_ids)

        pickings_to_update = picking

        if self.update_ic_pickings:
            for rec in ic_records:
                related_pickings = rec.picking_ids.filtered(lambda p: p.state not in ('cancel',) and p.picking_type_id.id != dropship_pick_type.id)
                msg_lang = rec.user_id.lang or rec.create_uid.lang if rec._name == 'sale.order' else rec.create_uid.lang
                msg_lang = msg_lang or self.env.user.lang or 'en_US'

                if related_pickings:
                    pickings_to_update |= related_pickings
                    rec.with_context(lang=msg_lang).message_post(body=_('Scheduled date has been changed to %s.') %(self.scheduled_date,), subject=_('Scheduled date info'))

        res = pickings_to_update.write({'scheduled_date': self.scheduled_date})
        return res

    @api.model
    def default_get(self, fields):
        res = super(InterCompanyScheduledDate, self).default_get(fields)
        ctx = self.env.context

        active_model = ctx.get('active_model', False)
        active_id = ctx.get('active_id', False)

        if active_model == 'stock.picking' and active_id:
            picking = self.env[active_model].browse(active_id)
            res['scheduled_date'] = picking.scheduled_date
            res['picking_id'] = active_id

        return res
