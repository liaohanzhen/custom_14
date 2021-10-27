# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import os
import datetime

from . import test
from . import SEPA_REPORT_OUTPUT_PATH

from odoo import fields, models
from odoo.tools.misc import formatLang

def _get_formated_amount(obj):
    ret_amount = formatLang(
        obj.with_context(lang='de_DE').env, obj.amount_residual, currency_obj=obj.currency_id)
    return ret_amount


class AccountMove(models.Model):
    _inherit = 'account.move'

    refund_type = fields.Selection(
        [('correction', 'Correction'), ('refund', 'Refund')],
        'Credit Note Type',
        default='correction',
        required=True
    )
    debitor_number = fields.Char(related='partner_id.commercial_partner_id.debitor_number')
    creditor_number = fields.Char(related='partner_id.commercial_partner_id.creditor_number')

    
    def _search_iban_number(self, partners):
        bank_account = self.env['res.partner.bank'].search([
            ('partner_id', 'in', partners.ids)
        ])

        return bank_account or self.env['res.partner.bank']
    
    def _search_customer_iban_number(self):
        return self._search_iban_number(self.partner_id)

    
    def _get_vendor_bank_bic(self):
        bank_account = self._search_customer_iban_number()

        return bank_account.bank_id and bank_account.bank_id.bic or ""

    
    def _get_user_company(self):
        return self.env.user.partner_id and self.env.user.partner_id.company_id

    
    def _get_user_company_bic(self):
        company = self.env.user.partner_id and self.env.user.partner_id.company_id
        company_partner = company.partner_id
        company_partner_bank_account = self._search_iban_number(company_partner)

        return company_partner_bank_account.bank_id and company_partner_bank_account.bank_id.bic or ""

    
    def _get_user_company_iban_number(self):
        user_company = self._get_user_company()
        return self._search_iban_number(user_company.partner_id)
    
    def get_sepa_report_data(self):
        self.ensure_one()

        sepa_report_data = {
           'ZielIban': self._search_customer_iban_number().acc_number or '',
           'ZielBic': self._get_vendor_bank_bic(),
           'Betrag': _get_formated_amount(self) or "",
           'Verw1': self.ref or "",
           'Verw2': '',
           'QuelleName': self._get_user_company().name or "",
           'QuelleIban': self._get_user_company_iban_number().acc_number or '',
           'Datum': datetime.date.today(),
           'QuelleInstitutKopie': self._get_user_company().name or "",
           'ZielIbanKopie': self._search_customer_iban_number().acc_number or '',
           'ZielBicKopie': self._get_vendor_bank_bic() or "",
           'BetragKopie': _get_formated_amount(self) or "",
           'QuelleInstitut': self._get_user_company().name or "",
           'UpperBic': self._get_user_company_bic() or "",
           'Verw1Kopie': self.ref or "",
           'Verw2Kopie': '',
           'QuelleNameKopie': self._get_user_company().name or "",
           'QuelleIbanKopie': self._get_user_company_iban_number().acc_number or '',
           'DatumKopie': datetime.date.today(),
           'ZielName': self.partner_id.name or "",
           'ZielNameKopie': self.partner_id.name or "",
           'UpperBicKopie': self._get_user_company_bic(),
        }
        return sepa_report_data

    
    def create_sepa_pdf_slip(self):
        for bill in self:
            AttModel = self.env['ir.attachment']
            sepa_report_data = bill.get_sepa_report_data()

            template_sepa_pdf = self.env.ref('frogblue_extensions.sepa_report_template_pdf')
            template_url = AttModel._full_path(template_sepa_pdf.store_fname)

            test.write_fillable_pdf(template_url, SEPA_REPORT_OUTPUT_PATH, sepa_report_data)

            with open(SEPA_REPORT_OUTPUT_PATH, "rb") as f:

                attachment = AttModel.create({
                    'name': _("Transfer voucher"),
                    'datas': base64.encodebytes(f.read()),
                    'res_model': self._name,
                    'res_id': int(self.id),
                    'type': 'binary'
                })

            os.remove(SEPA_REPORT_OUTPUT_PATH)
            return attachment

    
    def generate_and_attach_sepa_pdf_slip(self):
        self.ensure_one()

        self.create_sepa_pdf_slip()

        self.message_post(
            body=_("New transfer voucher has benn generated"
                 " and attached to the document by : %s") %
                 self.env.user.login)
        return self

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_id = fields.Many2one('account.asset', string='Asset', readonly=True)
