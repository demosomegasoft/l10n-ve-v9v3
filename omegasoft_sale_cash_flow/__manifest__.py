# -*- coding: utf-8 -*-
{
	'name': 'Omegasoft C.A Flujo de caja',
	'version': '2.0',
	'category': 'Accounting/Localizations/Account Charts',
	'author': 'Omegasoft C.A',
	'contributor': [
		'Naudy Mendez - naudy.mendez@omegasoftve.com',
	],
	'website': 'https://www.omegasoftve.com',
	'summary': 'Flujo de caja',
	'description': '''
Flujo de caja
=============
	''',
	'depends': [
		'l10n_ve_dual_currency',
	],
	'data': [
		'security/ir.model.access.csv',
		'security/security.xml',
		'views/cash_flow_report.xml',
	],
	'application': False,
	'installable': True,
	'auto_install': False,
	'license': 'LGPL-3',
}