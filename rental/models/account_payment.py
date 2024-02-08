from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
from odoo.tools.misc import file_open


class Payment(models.Model):
    _inherit = 'account.payment'

    rental_order_id = fields.Many2one('rental.order', ondelete='cascade')
