from odoo import api, models


class PatientCardReport(models.AbstractModel):
    _name = 'report.hospital.report_patient'
    _description = 'Get .'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("_get_report_values called".center(50, '-'))
        appointments = self.env['hospital.appointment'].search([('patient_id', '=', docids[0])]).read(
            ['name', 'notes', 'appointment_date'])
        print(appointments)
        return {
            'doc_ids': docids,
            'doc_model': self.env['hospital.patient'],
            'data': data,
            'appointments': appointments,
            'docs': self.env['hospital.patient'].browse(docids[0]),
        }

#
# class SaleOrderReport(models.AbstractModel):
#     _name = 'report.stock.report_picking'
#     _description = 'Get .'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         print("_get_report_values called for sales order pdf".center(50, '-'))
#         docs = self.env['stock.picking'].browse(docids[0])
#         print(docs)
#         return {
#             'doc_ids': docids,
#             'doc_model': self.env['sale.order'],
#             'data': data,
#             'docs': docs,
#         }
