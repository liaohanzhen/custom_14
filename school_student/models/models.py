# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random


class StudentAddress(models.Model):
    _name = 'student.address'
    _description = ''
    _rec_name = 'street'

    street = fields.Char(string='street')
    street_one = fields.Char(string='street_one')
    city = fields.Char(string='city')
    state = fields.Char(string='state')
    country = fields.Char(string='country')
    zip_code = fields.Char(string='zip_code')


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = ''
    _inherit = 'student.address'
    _rec_name = 'name'
    _order = 'school_id'  # order by
    # _description = 'school_student.school_student'


    roll_number = fields.Char(string='Roll number')
    name = fields.Char()

    currency_id = fields.Many2one('res.currency', string='Currency')
    student_fees = fields.Monetary(string='Fees')

    school_id = fields.Many2one('school.profile', string="School", domain="["
                                                                          "('school_type', '=', 'public'), "
                                                                          "('is_virtual_class', '=' , True)]")
    hobby_list = fields.Many2many('student.hobby', 'student_hobby_rel_table', 'student_id', 'hobby_id',
                                  string='Hobbies')
    active = fields.Boolean(string='Status', default=True)

    is_virtual_class = fields.Boolean(related='school_id.is_virtual_class', string='Online class')
    school_address = fields.Text(related='school_id.address', string='School Address')

    _sql_constraints = [
        ('student_fees_check', 'CHECK(student_fees > 0)', 'Enter greater than 50.'),
    ]

    @api.model
    def _change_roll_number(self, prefix):
        for std in self.search([('roll_number', '=', False)]):
            std.roll_number = prefix + str(std.id)

    def wiz_open(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'student.fees.update.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def custom_button_method(self):
        print("Custom method got called...")
        print(self._context)
        self.student_fees = random.randint(0, 10000)
        self.active = not self.active

    # def write(self, val):
    #     print("Write method got called..")
    #     print(self._context.get('data'))
    #     res = super().write(val)
    #     if not self.hobby_list:
    #         raise UserError("Select at list one hobby first..")
    #     return res

    def default_get(self, fields=None):
        print("fields", fields)
        res = super().default_get(fields)
        print("res", res)
        return res

    def name_get(self):
        return [(self.id, f"{self.name} - {self.roll_number}")]


class SchoolProfile(models.Model):
    _inherit = ['school.profile']

    school_list = fields.One2many('school.student', 'school_id', string='school list')

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     if not res.school_list:
    #         raise UserError("Add at list one student.")
    #     return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search(['|', '|', '|',
                                   ('name', operator, name), ('email', operator, name),
                                   ('school_rank', operator, name), ('school_type', operator, name), ])
            return records.name_get()
        # return self.search([('name', operator, name)] + args, limit=limit).name_get()
        return super().name_search(name, args, operator, limit)

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     domain = []
    #     print(domain)
    #     if name:
    #         domain = ['|', '|', ('name', operator, name),
    #                   ('email', operator, name), ('school_type', operator, name), ]
    #     results = self.search(domain+args, limit=limit)
    #     return results.name_get()


class Hobbies(models.Model):
    _name = 'student.hobby'

    name = fields.Char(string='Hobby name')


class Partner(models.Model):
    _inherit = ['res.partner', ]

    @api.model
    def create(self, vals):
        print("self.env....", self.env)
        print("self.vals....", vals)
        print("self.company....", self.env.company)
        print("self.companies....", self.env.companies)
        print("self.vals....", self.env.user, self.env.user.name)
        print("self.env.context....", self.env.context)
        return super().create(vals)


class SchoolStudentNew(models.Model):
    _inherit = 'school.student'

    parent_name = fields.Char(string='Parents Name', compute='_default_parent_name', store=True)

    @api.depends('name')
    def _default_parent_name(self):
        for std in self:
            print("_default_parent_name called.................")
            std.parent_name = std.name
