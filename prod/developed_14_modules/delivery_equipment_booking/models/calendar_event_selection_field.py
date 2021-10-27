# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SelectionBooking(models.Model):
    """ Model for Calendar Event
    """

    _name= 'selection.booking'
    
    name = fields.Char(string="Selection Booking")

class RequestRefer(models.Model):
    """ Model for Calendar Event
    """

    _name= 'request.refer'
    
    name = fields.Char(string="What does this request refer to?")

class Requirements(models.Model):
    """ Model for Calendar Event
    """

    _name= 'requirements'
    
    name = fields.Char(string="Requirements")
