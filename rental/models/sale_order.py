from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
from odoo.tools.misc import file_open


class Sale(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        super().action_confirm()
        for rec in self:
            for product in rec.order_line.mapped('product_id'):
                product.state = 'sold'
