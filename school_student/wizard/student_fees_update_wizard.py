from odoo import api, models, fields


class StudentFeesUpdateWizard(models.TransientModel):
    _name = 'student.fees.update.wizard'

    total_fees = fields.Float(string='Fees')

    def update_student_fees(self):
        print("============== update_student_fees =====================")
        print(self)
        print(self.total_fees)
        print(self._context.get('active_ids'))
        print(self._context.get('active_id'))
        self.env['school.student'].browse(self._context.get('active_ids')).update({'student_fees': self.total_fees})
        print(self.env['school.student'].browse(self._context.get('active_ids')).mapped('name'))
        return False

    @api.model
    def create(self, vals):
        print("Create method got called.....")
        return super().create(vals)
