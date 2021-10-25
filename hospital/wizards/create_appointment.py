from odoo import models, fields


class CreateAppointment(models.TransientModel):
    _name = 'create.appointment.wizard'

    patient_id = fields.Many2one('hospital.patient', string='Patient ID', required=True, tracking=True)
    appointment_date = fields.Date(string='Date', required=True, default=fields.Date.today())

    def create_appointment(self):
        vals = {
            'patient_id': self.patient_id.id,
            'appointment_date': self.appointment_date,
            'notes': 'created from wizard',
        }
        self.patient_id.message_post(body="Appointment creates successfully..", subject="Appointment")
        appointment = self.env['hospital.appointment'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hospital.appointment',
            'res_id': appointment.id,
            'context': {'form_view_initial_mode': 'edit'},
            # ----  OR  -----
            # 'context': context,
        }

    def get_data(self):
        print('------ get_data called ------')
        appointments = self.env['hospital.appointment'].search([])
        print(appointments)
        print(appointments.search_count([]))
        return {
            'name': 'Create Appointment',
            'res_model': 'create.appointment.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
            },
        }

    def delete_patient(self):
        print(" delete_patient ".center(50, '-'))
        for rec in self:
            print(rec.patient_id)
            rec.patient_id.unlink()

    def print_patient_report(self):
        print(" print_patient_report ".center(50, '-'))
        data = {
            'appointments': self.env['hospital.appointment'].search([('patient_id', '=', self.patient_id.id)]).read(
                ['name', 'appointment_date', 'state', 'notes']),
        }
        print(data['appointments'])
        return self.env.ref('hospital.report_patient_appointment').with_context(landscape=True).report_action(self,
                                                                                                              data=data)
