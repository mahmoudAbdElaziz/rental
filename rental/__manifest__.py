# -*- coding: utf-8 -*-
{
    'name': "Rental Management",
    'summary': "Rental Management",
    'category': 'sale',
    'version': '16.0.1',
    'depends': ['mail', 'account', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',

        'views/rental_order.xml',
        'views/product.xml',
        'views/customer.xml',
        'views/sales_man.xml',
        'views/account_payment.xml',

        'data/colors.xml',
        'data/product.xml',
        'data/ir_sequence_data.xml',

        'report/report_paperformat.xml',
        'report/rental_receipt_order.xml',
        'report/rental_detailed_order.xml',
    ],
}
