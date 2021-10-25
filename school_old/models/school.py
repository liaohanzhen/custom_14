from odoo import fields, models, api, _


class SchoolProfile(models.Model):
    _name = 'school.profile'
    _description = ''

    SCHOOL_TYPE = [
        ('public', 'Public School'),
        ('private', 'Private School')
    ]

    # name = fields.Char(string="School name", help="Enter your school name...", readonly=True)
    # name = fields.Char(string="School name", help="Enter your school name...", required=True, default="School Name", size=11)
    # default = set default value.
    # size = set max size of that field.
    # readonly = set field to readonly fields.
    # required = set field to required fields.
    # trim = default set to True remove extra spaces from sides. 
    # @api.depends = set field readonly user can't update it's value. 
    # @api.onchange = user can update it's value. The fields is not readonly. 
    # @api.model = use when we create a new model recordset. 

    def get_school_rank(self):
        return 200

    name_seq = fields.Char(string='School ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    name = fields.Char(string="School name", copy=False)
    email = fields.Char(string="School email", copy=False)
    phone = fields.Char(string="Phone")
    school_rank = fields.Integer(string="School Rank", default=get_school_rank)

    is_virtual_class = fields.Boolean(string="Online class", help="Mark true if his class is online class..")
    result = fields.Float(string="Result", digits=(2, 2))
    address = fields.Text(string="School address", help="This is school permanent address")

    # for html editor look add fields.Html or in XML add widget="html"
    school_description = fields.Html(string="Description")

    establish_date = fields.Date(string="Establish Date")
    open_date = fields.Datetime(string="Open Date", default=fields.Datetime.now())

    school_type = fields.Selection(SCHOOL_TYPE, string="School type", required=True, default="private")

    document = fields.Binary(string="Document", help="Upload your document..")
    document_name = fields.Char(string="Filename")
    image = fields.Image(string="Image", max_width=100, max_height=100)

    auto_rank = fields.Integer(string="Auto rank", compute='_auto_rank_populate', store=True)

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Enter unique email'),
        ('result_check', 'CHECK(result >= 50)', 'Enter result > 50..'),
    ]

    @api.depends('school_type')
    def _auto_rank_populate(self):
        # print(self.env['school.student'].fields_get(['email']))
        for rec in self:
            if rec.school_type == 'private':
                rec.auto_rank = 100
            elif rec.school_type == 'public':
                rec.auto_rank = 50
            else:
                rec.auto_rank = 0

    # @api.model
    # def name_create(self, name):
    #     print(name)
    #     return name

    def name_get(self):
        names = []
        for rec in self:
            names.append((rec.id, f"{rec.name} - {rec.school_type}"))
        return names

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('school.profile.sequence') or _('New')
        result = super(SchoolProfile, self).create(vals)
        return result
