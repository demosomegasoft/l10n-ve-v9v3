# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class AssociatedExpenses(models.Model):
	_name = 'ft.associated.expenses'
	_description = 'Associated expenses'

	shipping_company_id = fields.Many2one('ft.shipping.companies', string="Shipping company")
	storage_id = fields.Many2one('ft.storage', string="Warehouse", ondelete='restrict')
	route_id = fields.Many2one('ft.import.routes', string="Import route")
	forecast_id = fields.Many2one('ft.forecast', string="Forecast")
 
	product_id = fields.Many2one('product.template', string='Concept', required=True, domain=[('type','=','service'), ('landed_cost_ok', '=', True)], help="Indicates the service associated with the shipping company, such as general expenses")
	currency_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
	currency_ref_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
	fee = fields.Monetary(string="Fee", currency_field='currency_id', help="Indicates the daily amount for delay in the main currency configured")
	fee_ref = fields.Monetary(string="Fee ref", currency_field='currency_ref_id', help="Indicates the daily amount for delay in the configured secondary currency.")
	concept_type = fields.Selection(
     selection=[
			('sea_freight', 'Sea freight'),
			('land_freight', 'Land freight'),
			('sure', 'Sure'),
			('customs_expenses', 'Customs expenses'),
			('storage_expenses', 'Storage Expenses'),
			('general_expenses', 'General expenses'),
  		], 
    	string="concept type",
  		help="Indicates the type of associated service concept"
    )
	
	cost_type = fields.Selection(
    	selection=[
        	('import', 'Import'),
    		('nationalization', 'Nationalization')
        ],
     	string="cost type",
    	help="Indicates the type of cost of the associated Service"
    )
	
	@api.onchange('fee')
	def _onchange_amount(self):
		self.fee_ref = self.currency_id._convert(self.fee, self.currency_ref_id, self.env.company, datetime.now())

	@api.onchange('fee_ref')
	def _onchange_amount_ref(self):
		self.fee = self.currency_ref_id._convert(self.fee_ref, self.currency_id, self.env.company, datetime.now())
	
	@api.onchange('product_id')
	def _onchange_concept_type_cost_type(self):
		if self.product_id:
			self.concept_type = self.product_id.concept_type
			self.cost_type =  self.product_id.cost_type