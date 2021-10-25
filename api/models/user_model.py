import pandas
import requests

from odoo import fields, models


class UserModel(models.Model):
    _name = 'user.model'
    _description = 'UserModel'

    userId = fields.Char(string='Name')
    title = fields.Char(string='Title')
    body = fields.Html('Body')

    def load_data(self):
        data = requests.get('https://jsonplaceholder.typicode.com/posts')
        data = pandas.DataFrame(data.json())
        user_ids = pandas.Series(self.env['user.model'].search([('id', 'in', data.id.tolist())]).ids)
        data = data[~data.id.eq(user_ids)].T.to_dict().values()
        if data:
            self.env['user.model'].create(data)
