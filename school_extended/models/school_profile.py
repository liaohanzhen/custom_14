from odoo import models, fields, api


class SchoolStudent(models.Model):
    _inherit = 'school.student'
    _description = ''

    student_full_name = fields.Char(string='Full Name')
