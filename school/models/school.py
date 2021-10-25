from odoo import fields, models


class Schoolprofile(models.Model):
    _name = 'school.profile'

    name = fields.Char(string="school name")
    email = fields.Char(string="email")
    phone = fields.Char(string='phone')
    is_virtual_class = fields.Boolean(string='virtual class supported', help='this is boolean field')
    school_rank = fields.Integer(string="Rank", help='this is school rank field')
    address = fields.Text(string='Address')

    result = fields.Float(string='result', help='this is tool tip')
    estalish_date = fields.Date(string='establish date', default=fields.Date.today())
    open_date = fields.Datetime(string='open date', readonly=True)
    school_type = fields.Selection([('public', 'public school'),
                                    ('privat', 'privat school')], String="type of school")
    documents = fields.Binary(string='Documents')
    school_image = fields.Image(string='upload school image', max_height=100, max_width=100)
    school_description = fields.Html(string='discription')
    auto_rank = fields.Integer(compute='_auto_rank_populate', string='Auto Rank')
    currency_id = fields.Many2one('res.currency', string='Currency')

    # def _auto_rank_populate(self):
    #     for rec in self:
    #         if rec.school_type == 'privat':
    #             rec.auto_rank = 50
    #         elif rec.school_type == 'public':
    #             rec.auto_rank = 100
    #         else:
    #             rec.auto_rank=0
    #
    # @api.model
    # def name_create(self, name):
    #     print(self)
    #     print(name)
    #     rtn=self.create({'name':name})
    #     print(rtn)
    #     print('rtn.name_get()[0]', rtn.name_get())
    #     return rtn.name_get()[0]
    #
    # def name_get(self):
    #     student_list=[]
    #     for school in self:
    #         name=school.name
    #         if school.school_type:
    #             name+="({})".format(school.school_type)
    #             student_list.append((school.id,name))
    #     return student_list
