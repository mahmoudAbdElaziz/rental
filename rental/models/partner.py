from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
from odoo.tools.misc import file_open


class Customer(models.Model):
    _name = "res.customer"
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner')

    rental_ids = fields.One2many('rental.order', 'customer_id', domain=[('state', '!=', 'cancel')])


class SalesMan(models.Model):
    _name = "res.sales.man"
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner')

    rental_ids = fields.One2many('rental.order', 'sales_id', domain=[('state', '!=', 'cancel')])
