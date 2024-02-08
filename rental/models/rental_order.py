from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import ValidationError


class RenalOrder(models.Model):
    _name = 'rental.order'
    _description = 'Renal Order'
    _inherit = ['mail.thread']

    name = fields.Char(default="New", readonly=True, copy=False, string="Number")
    customer_id = fields.Many2one('res.customer', 'Customer', required=True)
    sales_id = fields.Many2one('res.sales.man', 'Sales', required=True)
    mobile = fields.Char(related='customer_id.mobile', readonly=False)
    date_from = fields.Date(default=lambda self: fields.Date.today(), required=True, string="From")
    date_to = fields.Date(default=lambda self: fields.Date.today() + relativedelta(days=3), required=True, string="To")
    confirmation_date = fields.Date(readonly=True, copy=False)
    pickup_date = fields.Date(readonly=True, copy=False)
    return_date = fields.Date(readonly=True, copy=False)
    is_late = fields.Boolean(readonly=True, string="Late", copy=False)
    line_ids = fields.One2many('rental.order.line', 'order_id', required=True)
    state = fields.Selection([('pending', 'Pending'),
                              ('confirm', 'Confirmed'),
                              ('pickup', 'Pickup'),
                              ('return', 'Returned'),
                              ('cancel', 'Cancelled')], default='pending', copy=False)
    paid_amount = fields.Integer(string='Paid', compute='_compute_amounts', )
    remainder_amount = fields.Integer(compute='_compute_amounts', string='Remainder')
    total_amount = fields.Integer(compute='_compute_amounts')
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    product_ids = fields.Many2many('product.product', compute='_compute_line_products', string="Products")
    payment_ids = fields.One2many('account.payment', 'rental_order_id')

    def action_register_payment(self):
        context = {'default_payment_type': 'inbound',
                   'default_partner_type': 'customer',
                   'default_rental_order_id': self.id,
                   'default_amount': self.remainder_amount,
                   'default_partner_id': self.customer_id.partner_id.id,
                   'default_move_journal_types': ('cash'),
                   'display_account_trust': True}
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('rental.account_payment_form').id,
            'type': 'ir.actions.act_window',
            'context': context
        }

    @api.depends('line_ids', 'line_ids.product_id')
    def _compute_line_products(self):
        for rec in self:
            rec.product_ids = rec.line_ids.mapped('product_id').ids

    def print_receipt(self):
        return self.env.ref('rental.rental_receipt_order').report_action(self)

    def print_detailed_order(self):
        return self.env.ref('rental.rental_detailed_order').report_action(self)

    def unlink(self):
        if self.state != 'cancel':
            raise ValidationError(_('Only canceled Order Can Be deleted'))
        return super(RenalOrder, self).unlink()

    @api.depends('payment_ids')
    def _compute_amounts(self):
        for rec in self:
            rec.paid_amount = sum(x.amount for x in rec.payment_ids)
            rec.total_amount = sum(x.price for x in rec.line_ids)
            rec.remainder_amount = rec.total_amount - rec.paid_amount

    @api.model
    def default_get(self, fields):
        defaults = super(RenalOrder, self).default_get(fields)
        if 'default_product_id' in self.env.context:
            product = self.env['product.product'].browse(self.env.context.get('default_product_id'))

            line = self.env['rental.order.line'].create({
                'product_id': product.id,
                'price': product.lst_price,
            })
            defaults['line_ids'] = line
        return defaults

    def cancel_action(self):
        self.write({'state': 'cancel'})

    def confirm_action(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Three is no products to be confirmed.'))
            rec.line_ids._check_dates()

            if not rec.name or rec.name == 'New':
                name = self.env['ir.sequence'].next_by_code('rental.order')
                rec.write({'name': name})
            rec.write({'state': 'confirm'})

    def pickup_action(self):
        for rec in self:
            if rec.line_ids:
                products = rec.line_ids.mapped('product_id')
                products.write({'state': 'out'})
            rec.write({'state': 'pickup'})

    def return_action(self):
        for rec in self:
            if rec.line_ids:
                products = rec.line_ids.mapped('product_id')
                products.write({'state': 'available'})
            rec.write({'state': 'return'})

    @api.constrains('date_from', 'date_to')
    def _check_rental_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_('The ending date must not be prior to the starting date.'))


class RenalOrderLine(models.Model):
    _name = 'rental.order.line'
    _description = 'Renal Order Line'

    order_id = fields.Many2one('rental.order', ondelete='cascade')
    customer_id = fields.Many2one(related='order_id.customer_id')
    mobile = fields.Char(related='customer_id.mobile')
    name = fields.Char(related='order_id.name')
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'rental'), ('state', '!=', 'sold')],
                                 required=True)
    price = fields.Integer()
    notes = fields.Char(string="Comments")
    year = fields.Selection(related='product_id.year')
    size = fields.Integer(related='product_id.size')
    color_id = fields.Many2one(related='product_id.color_id')
    model_id = fields.Many2one(related='product_id.model_id')
    brand_id = fields.Many2one(related='product_id.brand_id')
    barcode = fields.Char(related='product_id.barcode')
    date_from = fields.Date(related='order_id.date_from')
    date_to = fields.Date(related='order_id.date_to')
    state = fields.Selection(related='order_id.state')
    paid_amount = fields.Integer(related='order_id.paid_amount')
    remainder_amount = fields.Integer(related='order_id.remainder_amount')
    total_amount = fields.Integer(related='order_id.total_amount')

    _sql_constraints = [
        ('product_id_uniq', 'UNIQUE (order_id,product_id)', 'You can not Select sama product twice in sama order')
    ]

    def view_booking_action(self):
        return {
            'name': _('Booking'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'res_model': 'rental.order',
            'view_id': self.env.ref('rental.rental_order_view_form').id,
            'context': {'create': False},
            'target': 'new',
        }

    @api.onchange('product_id')
    def onchange_method(self):
        self.price = self.product_id.lst_price

    def _check_dates(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('state', 'in', ('confirm', 'pickup')),
                ('product_id', '=', rec.product_id.id),
                '|', '|',
                '&', ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_from),
                '&', ('date_from', '<=', rec.date_to), ('date_to', '>=', rec.date_to),
                '&', ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_to),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(_('Sorry This Product is Booked in This Period. Please reschedule the period'))
