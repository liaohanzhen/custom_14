from odoo import api, fields, models


# class AccountMoveInvoiceReport(models.Model):
#     _name = 'report.account.report_invoice_with_payments'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         print(docids)
#         return {
#             'doc_ids': docids,
#             'data': data,
#             'docs': self.env['account.move'].browse(docids[0]),
#         }
