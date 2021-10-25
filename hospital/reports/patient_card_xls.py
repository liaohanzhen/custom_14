from odoo import models


class PatientCardXlsx(models.AbstractModel):
    _name = 'report.hospital.report_patient_xls'
    _inherit = 'report.report_xlsx.abstract'

    def appointment_data(self, sheet, partners, df):
        patient = partners[0]
        appointments = self.env['hospital.appointment'].search([('patient_id', '=', patient)])
        sheet.set_column('A0:E0', 15)
        sheet.write(0, 0, 'ID')
        sheet.write(0, 1, 'Patient Name')
        sheet.write(0, 2, 'Appointment Date')
        sheet.write(0, 3, 'Notes')
        for key, val in enumerate(appointments):
            key += 2
            sheet.write(key, 0, val.name)
            sheet.write(key, 1, val.patient_id.patient_name)
            sheet.write(key, 2, val.appointment_date, df)
            sheet.write(key, 3, val.notes)

    def generate_xlsx_report(self, workbook, data, partners):
        print("--------------- generate_xlsx_report ------------------", data)
        sheet = workbook.add_worksheet('Patient Card')
        # sheet.right_to_left()
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        column = ['name_seq', 'gender', 'patient_name', 'email', 'patient_age', 'doctor_id', 'age_group', 'notes', ]
        if data.get('appointment', False):
            self.appointment_data(sheet, partners.ids, date_format)
            return
        for key, val in enumerate(column):
            sheet.set_column(0, key, len(val) + 15)
            sheet.write(0, key, val, bold)
        for key, obj in enumerate(partners):
            key += 1
            sheet.write(key, 0, obj.name_seq)
            sheet.write(key, 1, obj.gender)
            sheet.write(key, 2, obj.patient_name)
            sheet.write(key, 3, obj.email)
            sheet.write(key, 4, obj.patient_age)
            sheet.write(key, 5, obj.doctor_id.doctor_name)
            sheet.write(key, 6, obj.age_group)
            sheet.write(key, 7, obj.notes)
