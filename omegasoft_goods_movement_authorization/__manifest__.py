# -*- coding: utf-8 -*-
{
    'name': "Omegasoft Goods Movement Authorization",
    'summary': """Goods Movement Authorization""",
    'description': """
    """,
    'author': 'Omegasoft C.A',
    'website': 'https://www.omegasoftve.com/',
    'category': 'Stock',
    'version': '0.1',
    'depends': ['stock', 'fleet', 'omegasoft_dispatch_control'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/goods_movement_authorization.xml',
    ],
    'license': 'LGPL-3'
}