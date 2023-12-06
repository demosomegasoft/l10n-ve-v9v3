from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo import _


def _create_data_containers_companys(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    base_company = env.ref('base.main_company')
    containers = env['ft.containers'].search([])
    for company in companies:
        if company != base_company:
            for container in containers:
                env['ft.containers'].create([{
                    'name': container.name,
                    'code':container.code ,
                    'inside_length': container.inside_length,
                    'inside_width': container.inside_width,
                    'inside_height':container.inside_height,
                    'door_height':container.door_height,
                    'door_width':container.door_width,
                    'cubic_capacity':container.cubic_capacity,
                    'tare':container.tare,
                    'maximum_load':container.maximum_load,
                    'company_id': company.id,
                    'delete_container': container.delete_container,
                }])
    _create_tax(env)
                
def _create_tax(env):
    companies = env['res.company'].search([])
    for company in companies:
        if not company.country_id:
            raise UserError(_("The company does not have a configured country."))
        env['account.tax'].create([{
            'name': 'TSA',
            'amount_type': 'percent',
            'type_tax_use': 'tsa',
            'fiscal_tax_type': 'general',
            'amount': 0.5,
            'country_id': company.country_id.id,
            'company_id': company.id,
            'delete_tax': True
        },
        {
            'name': 'TSS',
            'amount_type': 'percent',
            'type_tax_use': 'tss',
            'fiscal_tax_type': 'general',
            'amount': 0.5,
            'country_id': company.country_id.id,
            'company_id': company.id,
            'delete_tax': True
        }])
        
def _uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    taxes = env['account.tax'].search([
        ('type_tax_use', 'in', ['tsa', 'tss']),
        ('delete_tax', '=', True),
    ])
    for tax in taxes:
        tax.delete_tax = False
    taxes.unlink()
