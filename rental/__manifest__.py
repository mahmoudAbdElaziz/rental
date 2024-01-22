# -*- coding: utf-8 -*-
{
    'name': "Rental Management",
    'summary': "Rental Management",
    'category': 'sale',
    'version': '16.0.1',
    'depends': ['account', 'sale'],
    'data': [
        'security/ir.model.access.csv',

        'views/rental_order.xml',
        'views/product.xml',

        'data/colors.xml',
        'data/product.xml',
        'data/ir_sequence_data.xml',

        'report/report_paperformat.xml',
        'report/rental_receipt_order.xml',
    ],
}
