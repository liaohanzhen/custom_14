from odoo import models, api, fields, _


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _rec_name = 'doctor_name'

    name = fields.Char(string='Doctor ID', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    doctor_name = fields.Char(string='Doctor Name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    user_id = fields.Many2one('res.users', string='Related User')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.doctor.sequence') or _('New')
        print("------ doctor Create called... -----")
        result = super().create(vals)
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search(['|', '|', ('name', operator, name), ('doctor_name', operator, name),
                                   ('user_id.name', operator, name), ])
            return records.name_get()
        # return self.search([('name', operator, name)] + args, limit=limit).name_get()
        return super().name_search(name, args, operator, limit)
