# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
	_inherit = "res.company"
	
	capacities_container = fields.Boolean(string="Capacities per Container", default=False,
                            help="It allows to establish the measurement by containers in the calculations of the cost structure of products." )

	import_purchase_tax = fields.Many2one('account.tax', string='Default Purchase Tax', domain="[('type_tax_use', '=', 'purchase')]")


	#create tax in company
	@api.model_create_multi
	def create(self, vals_list):
		companys = super().create(vals_list)
		for company in companys:
			if not company.country_id:
				raise UserError(_("The company does not have a configured country."))
			self.env['account.tax'].sudo().create([{
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
		return companys