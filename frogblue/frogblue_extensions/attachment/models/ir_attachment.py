# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    parent_id = fields.Many2one('ir.attachment', string='Parent Document')
    type_id = fields.Many2one('ir.attachment.types', string='Document Type')
    tag_ids = fields.Many2many('ir.attachment.tags', string='Document Tags')
    note = fields.Text('Document Note')
    summary = fields.Char('Summary')
    partner_id = fields.Many2one('res.partner', string='Partner', compute='_compute_partner_id', store=True)

    @api.onchange('res_model', 'res_id')
    def _compute_partner_id(self):
        for rec in self:
            if rec.res_model == 'res.partner':
                rec.partner_id = self.env['res.partner'].browse([rec.res_id])

    @api.model
    def create(self, vals):
        if vals.get('res_model') and vals['res_model'] == 'res.partner':
            vals['partner_id'] = vals['res_id']
        return super(IrAttachment, self).create(vals)


class IrAttachmentTypes(models.Model):
    _name = 'ir.attachment.types'
    _description = 'Attachment Types'

    name = fields.Char(string='Name')


class IrAttachmentTags(models.Model):
    _name = 'ir.attachment.tags'
    _description = 'Attachment Tags'

    name = fields.Char(string='Name')

