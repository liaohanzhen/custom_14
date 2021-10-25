# -*- coding: utf-8 -*-

from odoo import models, _


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    # Override original method
    def _create_invoice_cfdi_attachment(self, invoice, data):
        cfdit = {
            'in_invoice': 'Bill',
            'in_refund': 'Bill-Refund',
            'out_invoice': 'Invoice',
            'out_refund': 'Invoice-Refund'
        }
        cfdi_filename = ("%s-%s-MX-%s.xml" % (
            invoice.journal_id.code, invoice.payment_reference,
            cfdit.get(invoice.move_type))).replace('/', '')
        description = (_('Mexican %s CFDI generated for the %s document.') % (cfdit.get(invoice.move_type), invoice.name))

        return self._create_cfdi_attachment(cfdi_filename, description, invoice, data)