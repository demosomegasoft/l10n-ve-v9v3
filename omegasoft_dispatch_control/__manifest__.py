# -*- coding: utf-8 -*-
{
    'name': "Omegasoft dispatch control",
    'summary': """Omegasoft dispatch control""",
    'description': """Dispatch control records, created from sale orders invoice""",
    'author': "Omegasoft C.A",
    'website': "https://www.omegasoftve.com/",
    'category': 'Stock',
    'version': '1.0',
    'depends': ['sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/sequence.xml',
        'views/dispatch_control_views.xml',
    ],
    'license': 'LGPL-3',
}
