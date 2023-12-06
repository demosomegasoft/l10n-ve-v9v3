# -*- coding: utf-8 -*-
{
    'name': 'Omegasoft C.A Foreing trade',
    'version': '1.0',
    'category': 'Foreing trade',
    'application': False,
    'author': 'Omegasoft C.A',
    'website': 'https://www.omegasoftve.com/',
    'summary': 'Imports',
    'description': """
Comercio Exterior / Importaciones
=================================
* Administrar la operación logística, controlar y hacer el seguimiento de las compras internacionales cumpliendo con estándares de la legislación internacional
	""",
    'depends': ['base', 'product', 'purchase', 'sale_management', 'contacts' , 'account', 'l10n_ve_config_account', 'l10n_ve_dual_currency', 'l10n_ve_fiscal_identification', 'stock_landed_costs', 'stock_enterprise', 'l10n_ve_fiscal_book_report'],
    'data': [
        'data/sequence.xml',
        'security/company_rules.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/views.xml',
        'views/search_views.xml',
        'views/ft_shipping_companies.xml',
        'views/ft_ports.xml',
        'views/ft_duty.xml',
        'views/ft_agreement.xml',
        'views/ft_certificate_type.xml',
        'views/ft_certificate.xml',
        'views/ft_novelty_type.xml',
        'views/ft_containers.xml',
        'data/ft_containers_data.xml',
        'views/ft_storage.xml',
        'views/ft_import_routes.xml',
        'views/incoterms.xml',
        'views/res_partner.xml',
        'views/ft_label.xml',
        'views/ft_import.xml',
        'views/purchase_order.xml',
        'views/purchase_requisition_views.xml',
        'views/account_tax.xml',
        'views/account_move.xml',
        'views/ft_forecast.xml',
        'data/mail_template_data.xml',
        'views/res_config_settings_views.xml',
        
    ],
    'post_init_hook': '_create_data_containers_companys',
    'uninstall_hook': '_uninstall_hook',
    'license': 'LGPL-3'
}
