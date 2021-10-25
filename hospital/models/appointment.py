import random

from odoo import api, models, fields, _


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _rec_name = "name"
    # _order = 'name desc'
    _order = 'appointment_date'

    appointment_lines = fields.One2many('hospital.appointment.lines', 'appointment_id', string='Appointment Lines')
    name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient ID', required=True, tracking=True)
    patient_age = fields.Integer(string='Patient Age', related='patient_id.patient_age')
    amount = fields.Float(string='Amount')
    notes = fields.Text(string='Registration Note')
    doctor_note = fields.Text(string='Doctor Prescription')
    pharmacy_note = fields.Text(string='Pharmacy Note')
    appointment_date = fields.Date(string='Date', required=True, default=fields.Date.today())
    appointment_datetime = fields.Datetime(string='Datetime', required=True, default=fields.Datetime.now())
    product_id = fields.Many2one('product.template', string='Product Template')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status', required=True, default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Partner')
    order_id = fields.Many2one('sale.order', string='Sale Order')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            lines = [(5, 0, 0)]
            for line in rec.product_id.product_variant_ids:
                vals = {
                    'product_id': line.id,
                    'product_qty': 5,
                }
                lines.append((0, 0, vals))
            rec.appointment_lines = lines

    @api.onchange('partner_id')
    def onchange_method(self):
        for rec in self:
            print("called----", rec.partner_id.id)
            return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')

        result = super().create(vals)
        return result

    @api.model
    def _update_amount(self):
        print("called")
        for rec in self.env['hospital.appointment'].search([]):
            rec.amount = random.randint(1111, 99999)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Appointment is done..',
                    'type': 'rainbow_man',
                }
            }

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def delete_lines(self):
        print("------- delete_lines called ---------")
        for rec in self:
            print(rec.appointment_lines)
            rec.appointment_lines = [(5, 0, 0)]
            print(rec.appointment_lines)
            # a = self.env['hospital.appointment.lines'].search([])[3:]
            # rec.appointment_lines = [(6, 0, a.ids)]
            # print(rec.appointment_lines)


class HospitalAppointmentLines(models.Model):
    _name = 'hospital.appointment.lines'
    _description = 'Hospital Appointment Lines'

    product_id = fields.Many2one('product.product', string='Medicine')
    product_qty = fields.Integer(string='Product QTY')
    sequence = fields.Integer(string='Sequence')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment ID')
