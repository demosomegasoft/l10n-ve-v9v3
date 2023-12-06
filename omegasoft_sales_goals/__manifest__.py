# -*- coding: utf-8 -*-
{
	'name': "Omegasoft Sales Goals",
	'summary': """Omegasoft Sales Goals""",
	'description': """management of sales goals by user""",
	'author': "Omegasoft C.A",
	'website': "https://www.omegasoftve.com/",
	'category': 'Sale/CRM',
	'version': '1.0',
	'depends': ['web', 'crm'],
	'data': [
		'security/ir.model.access.csv',
		'security/company_rules.xml',
		'views/sales_goal_views.xml',
		'report/sales_goal_lines_report.xml',
	],
	'license': 'LGPL-3',
}