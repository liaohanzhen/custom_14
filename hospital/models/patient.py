# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import random

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _rec_name = "patient_name"

    name = fields.Char(string='Test')
    patient_name = fields.Char(string='Patient Name', required=True)
    patient_name_upper = fields.Char(string='Patient Name Upper', compute="compute_upper_name",
                                     inverse='inverse_upper_name')
    patient_age = fields.Integer(string='Patient Age', tracking=True, group_operator=False)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    age_group = fields.Selection([('major', 'Major'), ('minor', 'Minor')],
                                 string='Age Group', compute='_set_age_group', store=True)
    notes = fields.Text(string='Notes')
    email = fields.Char(string='Email')
    name_seq = fields.Char(string='Patient ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    image = fields.Binary(string='Image')
    active = fields.Boolean(string='Active', default=True)

    appointment_count = fields.Integer(string='Appointment', compute='get_appointment_count')

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor Name')
    doctor_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Doctor Gender',
                                     compute="doctor_gender_change")
    user_id = fields.Many2one('res.users', string='PRO')
    progress = fields.Float(string='Progress')

    @api.depends('patient_name')
    def compute_upper_name(self):
        for rec in self:
            rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False

    def inverse_upper_name(self):
        for rec in self:
            rec.patient_name = rec.patient_name_upper.lower() if rec.patient_name_upper else False

    @api.onchange('doctor_id')
    def doctor_gender_change(self):
        for rec in self:
            rec.doctor_gender = rec.doctor_id.gender

    def get_appointment_count(self):
        count = self.env['hospital.appointment'].search_count([('patient_id', '=', self.id)])
        self.appointment_count = count

    @api.depends('patient_age')
    def _set_age_group(self):
        for rec in self:
            rec.progress = round(random.random() * 100, 2)
            if rec.patient_age > 18:
                rec.age_group = 'major'
            else:
                rec.age_group = 'minor'

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')
        print("------ patient Create called... -----")
        result = super(HospitalPatient, self).create(vals)
        return result

    @api.constrains('patient_age')
    def check_age(self):
        for rec in self:
            if rec.patient_age <= 5:
                raise ValidationError(_('Error from @api.constrains: The age must be greater than 5...'))

    def open_patient_appointments(self):
        return {
            'name': 'Appointments',
            'domain': [('patient_id', '=', self.id)],
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def test_name(self):
        return {
            'name': 'Create Appointment',
            'res_model': 'create.appointment.wizard',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_send_card(self):
        template = self.env.ref('hospital.mail_template_hospital_patient')
        # print('template_id', template_id)
        # template = self.env['mail.template'].browse(template_id)
        # print('template', template)
        # template.send_mail(self.id, force_send=True, )
        # '''
        # This function opens a window to compose an email, with the emai template message loaded by default
        # '''
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': template,
            'target': 'new',
            'context': {
                'default_composition_mode': 'mass_mail' if len(self.ids) > 1 else 'comment',
                'default_res_id': self.ids[0],
                'default_model': 'hospital.patient',
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'website_sale_send_recovery_email': True,
                'active_ids': self.ids,
            },
        }

    def name_get(self):
        result = []
        print(self._context)
        for rec in self:
            result.append((rec.id, f"{rec.name_seq} - {rec.patient_name}",))
        print("--- name_get ---", result)
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search(['|', ('name_seq', operator, name), ('patient_name', operator, name), ])
            return records.name_get()
        # return self.search([('name', operator, name)] + args, limit=limit).name_get()
        return super().name_search(name, args, operator, limit)

    def check_patient_status(self):
        print('-------- check_patient_status called -------- ', self, sep='\n')

    def print_pdf_button(self):
        print('print_pdf_button'.center(50, '-'))
        return self.env.ref('hospital.report_hospital_patient').report_action(self)

    def print_xlsx_button(self):
        print('print_xlsx_button'.center(50, '-'))
        data = {
            'appointment': True,
        }
        return self.env.ref('hospital.report_hospital_patient_xls').report_action(self, data=data)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    patient_name = fields.Many2one('hospital.patient', string='Patient Name')

    def from_hospital(self):
        print("from_hospital".center(50, '-'))
        pass


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(selection_add=[('patient', 'Patient'), ])

    @api.model
    def create(self, vals):
        print("------ Create method got called from hospital.patient model -----")
        return super().create(vals)
