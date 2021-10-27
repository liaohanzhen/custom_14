# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import base64


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opentrans_order_transmitted = fields.Boolean('Order Transmitted')
    opentrans_order_not_send = fields.Boolean('Not transmit Order')

    @api.onchange('partner_id')
    def check_send_opentrans_order(self):
        if self.partner_id.not_transmit_order:
            self.opentrans_order_not_send = True

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.partner_id.not_transmit_order or not self.env.company.transmit_order_url:
            res.update({'opentrans_order_not_send': True})
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        opentrans = self.env['open.trans.sale.order']
        responsecode = errors = False
        for order in self:
            if not order.opentrans_order_not_send and self.env.company.transmit_order_url:
                xml_order, responsecode, statuscode, statustext, message, errors = opentrans.send_order_xml(order)
    
                if xml_order:
                    datas = base64.encodebytes(xml_order)
                    name = self.name + '.xml'
                    self.env['ir.attachment'].create({
                        'name': name,
                        'datas': datas,
                        'res_model': 'sale.order',
                        'res_id': order.id,
                    })

            msg = _('<b>OpenTrans Order API Status<b/>:<br/>')
            if responsecode and responsecode == 200:
                if statuscode == '200':
                    msg += _('Order transmitted<br/>')
                    self.write({'opentrans_order_transmitted': True,})
                else:
                    msg += _('Order not transmitted<br/>')
                msg += _('Status: %s - %s<br/>' % (statuscode, statustext))
                msg += '%s<br/>' % message
                if errors:
                    msg += '%s' % errors
            elif responsecode:
                msg += _('Connection Error - Order not transmitted<br/>')
            elif not self.opentrans_order_not_send:
                msg += _('Customer is set to not transmit Orders<br/>')
            if errors:
                msg += '%s' % errors
            if msg:
                self.message_post(body=msg)
            

        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        name = self.name + '.xml'
        xml_order = self.env['ir.attachment'].search([('name', '=', name)])
        if xml_order:
            xml_order.unlink()
        return res

