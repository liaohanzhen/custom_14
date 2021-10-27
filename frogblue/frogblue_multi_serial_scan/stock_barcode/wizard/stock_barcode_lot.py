# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import re


class StockBarcodeLot(models.TransientModel):
    _inherit = "stock_barcode.lot"

    product_tracking = fields.Selection('Product tracking type', related='product_id.tracking')
    scanned_barcode_lot_line_ids = fields.One2many('stock_barcode.scanned.line', 'stock_barcode_lot_id')
    scanned_qty_done = fields.Float()

    def on_barcode_scanned(self, barcode):
        if self.product_id.tracking != 'serial':
            return super(StockBarcodeLot, self).on_barcode_scanned(barcode)

        packages_regex = self.env['ir.config_parameter'].sudo().get_param('packages.barcode.regex', default=False)
        barcodes_splitter = self.env['ir.config_parameter'].sudo().get_param('packages.barcode.splitter', default=False)
        scanned_barcodes = [barcode]

        if packages_regex and barcodes_splitter:
            packages_regex = packages_regex.format(**{'splitter_plholder': barcodes_splitter})

            if re.match(packages_regex, barcode):
                barcode_parts = barcode.split('?')

                if len(barcode_parts) == 2:
                    scanned_barcodes = [barcode_parts[1]]
                else:
                    scanned_barcodes = barcode.split(barcodes_splitter)

        for bc in scanned_barcodes:
            suitable_line = self.scanned_barcode_lot_line_ids.filtered(lambda l: l.lot_name == bc or not l.lot_name)
            vals = {}
            if suitable_line:
                if suitable_line[0].lot_name and self.product_id.tracking == 'serial' and suitable_line[0].qty_done > 0:
                    raise UserError(_('You cannot scan two times the same serial number'))
                else:
                    vals['lot_name'] = bc
                vals['qty_done'] = suitable_line[0].qty_done + 1
                suitable_line[0].update(vals)
            else:
                vals['lot_name'] = bc
                vals['qty_done'] = 1
                vals['stock_barcode_lot_id'] = self.id
                self.env['stock_barcode.scanned.line'].new(vals)

            self.update({'scanned_qty_done': self.scanned_qty_done + 1})

        return

    def _update_scanned_quantity_done(self):
        self.scanned_qty_done = sum(self.scanned_barcode_lot_line_ids.mapped('qty_done'))

    def _adjust_lots(self):
        if self.product_id.tracking != 'serial':
            return False

        new_scanned_lines = self.env['stock_barcode.scanned.line']
        processed_wizard_lines = self.env['stock_barcode.lot.line']

        for scanned_line in self.scanned_barcode_lot_line_ids:
            existing = self.stock_barcode_lot_line_ids.filtered(lambda el: el.lot_name == scanned_line.lot_name)
            if existing:
                existing.write({'qty_done': scanned_line.qty_done})
                self.write({'qty_done': self.qty_done + 1})
                processed_wizard_lines |= existing
            else:
                new_scanned_lines |= scanned_line

        processed_wizard_line_ids = processed_wizard_lines.ids

        for scanned_line in new_scanned_lines:
            suitable_line = self.stock_barcode_lot_line_ids.filtered(lambda el: el.id not in processed_wizard_line_ids)

            if suitable_line:
                suitable_line[0].write({'qty_done': scanned_line.qty_done, 'lot_name': scanned_line.lot_name})
                processed_wizard_line_ids.append(suitable_line[0].id)
            else:
                raise ValidationError(_('Quantities does not match!'))

        wizard_lines_to_unlink = self.stock_barcode_lot_line_ids.filtered(lambda el: el.id not in processed_wizard_line_ids)
        if wizard_lines_to_unlink:
            wizard_lines_to_unlink.unlink()

        return True

    def validate_lot(self):
        self._adjust_lots()
        res = super(StockBarcodeLot, self).validate_lot()
        return res

class StockBarcodeLotLine(models.TransientModel):
    _name = "stock_barcode.scanned.line"
    _description = "Line of LN/SN scanned of a product"

    lot_name = fields.Char('Lot')
    qty_done = fields.Float('Scanned')
    stock_barcode_lot_id = fields.Many2one('stock_barcode.lot')

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        if self.stock_barcode_lot_id.product_id.tracking == 'serial' and self.qty_done > 1:
            raise UserError(_('You cannot scan two times the same serial number'))
        self.stock_barcode_lot_id._update_scanned_quantity_done()
