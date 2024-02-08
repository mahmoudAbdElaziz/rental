from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
from odoo.tools.misc import file_open


class Product(models.Model):
    _inherit = 'product.product'
    _order = 'barcode'

    def years_selection(self):
        year_list = []
        for y in range(datetime.now().year - 2, datetime.now().year + 10):
            year_list.append((str(y), str(y)))
        return year_list

    def _get_default_year(self):
        return str(datetime.now().year)

    @api.model
    def _default_image(self):
        return base64.b64encode(file_open('rental/static/src/img/dress.png', 'rb').read())

    image_1920 = fields.Image(default=_default_image)
    size = fields.Integer(default=45)
    year = fields.Selection(years_selection, string="Year", default=_get_default_year)
    color_id = fields.Many2one('product.color')
    model_id = fields.Many2one('product.model')
    brand_id = fields.Many2one('product.brand')
    state = fields.Selection([('available', 'Available'), ('out', 'Out Stock'), ('sold', 'Sold'), ],
                             default='available')
    rental_line_ids = fields.One2many('rental.order.line', 'product_id', domain=[('order_id', '!=', False)])
    booking_count = fields.Integer(compute='_compute_booking_count')
    type = fields.Selection([('rental', 'Rental'), ('sale', 'Sale')], default='rental')

    @api.depends('rental_line_ids')
    def _compute_booking_count(self):
        for rec in self:
            orders = self.env['rental.order.line'].search([('product_id', '=', self.id)]).mapped('order_id')
            rec.booking_count = len(orders)

    def selling_action(self):
        self.write({'state': 'sold'})

    def back_action(self):
        self.write({'state': 'available'})

    def booking_action(self):
        return {
            'name': _('Booking'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rental.order',
            'view_id': self.env.ref('rental.rental_order_view_form').id,
            'context': {'default_product_id': self.id},
        }

    def open_booking_list(self):
        orders = self.env['rental.order.line'].search([('product_id', '=', self.id)]).mapped('order_id')
        return {
            'name': _('Booking'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'rental.order',
            'domain': [('id', 'in', orders.ids)],
            'context': {'create': False},
        }


class ProductBrand(models.Model):
    _name = "product.color"
    _description = "Product Color"
    _order = 'sequence'

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = 'sequence'

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)


class ProductModel(models.Model):
    _name = 'product.model'
    _description = "Product Model"
    _order = 'sequence'

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)
