# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FtForecast(models.Model):
	_name = 'ft.forecast'
	_description = 'Import foreign trade forecast'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
	_order = 'import_id desc'

	import_id = fields.Many2one('ft.import', string="Import")
	state = fields.Selection(related="import_id.state")
	company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                    help='Company', default=lambda self: self.env.company)
	
	capacities_container = fields.Boolean(related='company_id.capacities_container')
 
	nationalization_rate = fields.Float(string="Nationalization rate",
                            help="It serves as the basis for calculating the amount for tax concepts in the forecast.")
	currency_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
	value_or = fields.Monetary(string="OR value", currency_field='currency_id', compute='_compute_values_forecast', store=True, readonly=True,
                            help="Indicates the total value of the Purchase Orders associated with the import folio in the main currency configured for the company")
	currency_ref_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
	value_or_ref = fields.Monetary(string="OR value ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                            help="Indicates the total value of the Purchase Orders associated with the import folio in the reference currency configured for the company.")
	
	ad_valorem = fields.Monetary(string="Ad Valorem", currency_field='currency_id', compute='_compute_values_forecast', store=True, readonly=True,
                            help="Indicates the total tax value of the products in the import process based on the tariffs configured on the product")
	ad_valorem_ref = fields.Monetary(string="Ad Valorem ref", currency_field='currency_ref_id',compute='_compute_values_forecast', store=True, readonly=True,
                                help="Indicates the value of the total tax of the products in the import process based on the tariffs configured in the product, in the reference currency")
	
	tsa = fields.Monetary(string="TSA", currency_field='currency_id', compute='_compute_values_forecast', store=True, readonly=True,
                       help="Indicates the value of the total tax of Fees for customs service related to the import process")
	tsa_ref = fields.Monetary(string="TSA ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                           help="Indicates the value of the total tax of Fees for customs service related to the import process")
	
	tss = fields.Monetary(string="TSS", currency_field='currency_id', compute='_compute_values_forecast', store=True,  readonly=True,
                       help="")
	tss_ref = fields.Monetary(string="TSS ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                           help="")
 
	iva = fields.Monetary(string="IVA", currency_field='currency_id', compute='_compute_values_forecast', store=True,  readonly=True,
                       help="")
	iva_ref = fields.Monetary(string="IVA ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                           help="")
	
	amount_for_delay = fields.Monetary(string="Amount for Delay", currency_field='currency_id', compute='_compute_values_forecast', store=True, readonly=True,
                                    help="")
	amount_for_delay_ref = fields.Monetary(string="Amount for Delay ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                                        help="")
	storage_delay = fields.Monetary(string="Storage Delay", currency_field='currency_id', compute='_compute_values_forecast', store=True, readonly=True,
                                help="")
	storage_delay_ref = fields.Monetary(string="Storage Delay ref", currency_field='currency_ref_id', compute='_compute_values_forecast', store=True, readonly=True,
                                     help="")
	# Gastos asociados
	associated_expenses_ids = fields.One2many('ft.associated.expenses', 'forecast_id', string="Associated expenses", compute="_associated_expenses_ids", store=True)
	
	# Formulacion
	split_method = fields.Selection([
    		('by_weight', 'By weight'),
			('by_volume', 'By volume'),
   			('by_Container', 'Units by Container')], required=True, default='by_weight', string="Division Method",
                            help="")

	container_type_id = fields.Many2one('ft.containers', string="Container type", domain=[('active_container', '=', True)], 
                            help="")
 
	number_container = fields.Integer(string="Container number",
                                    help="")

	#products associated with purchase
	forecast_product_ids = fields.One2many('ft.forecast.product', 'forecast_id', string="Products")

	@api.constrains('split_method')
	def value(self):
		if self.split_method == 'by_Container':
			if self.number_container == 0 or not self.container_type_id:
				raise UserError(_("Cannot calculate bin split method value if bin count is 0"))

	@api.depends('import_id.purchase_ids', 'split_method', 'nationalization_rate')
	def _compute_values_forecast(self):
		#Value OR
		self.value_or = sum([purchase.currency_id._convert(purchase.amount_untaxed, self.currency_id, purchase.company_id, purchase.date_order)
								for purchase in self.import_id.purchase_ids])
  
		self.value_or_ref = sum([purchase.currency_id._convert(purchase.amount_untaxed, self.currency_ref_id, purchase.company_id, purchase.date_order)
								for purchase in self.import_id.purchase_ids])
		#valorem
		self.ad_valorem = sum([(purchase.currency_id._convert(purchase.price_unit, self.currency_id, purchase.company_id, purchase.date_order) * purchase.product_qty) * purchase.product_id.rate_duty / 100
								for purchase in self.import_id.purchase_ids.order_line.filtered(lambda x: x.product_id.detailed_type == 'product')])
  
		self.ad_valorem_ref = self.ad_valorem / self.nationalization_rate if self.currency_id == self.env.ref('base.VES') else self.ad_valorem * self.nationalization_rate
		
		#tsa
		tsa = self.env['account.tax'].search([('type_tax_use', '=', 'tsa'), ('delete_tax', '=', True)], limit=1)
		self.tsa = self.value_or * tsa.amount
		self.tsa_ref = self.tsa / self.nationalization_rate if self.currency_id == self.env.ref('base.VES') else self.tsa * self.nationalization_rate
		
  		#tss
		tss = self.env['account.tax'].search([('type_tax_use', '=', 'tss')], limit=1)
		self.tss = self.value_or * tss.amount
		self.tss_ref = self.tss / self.nationalization_rate if self.currency_id == self.env.ref('base.VES') else self.tss * self.nationalization_rate
  
		#iva
		import_purchase = self.env.company.import_purchase_tax.amount
		self.iva = self.value_or * import_purchase if import_purchase else 0
		self.iva_ref = self.iva / self.nationalization_rate if self.currency_id == self.env.ref('base.VES') else self.iva * self.nationalization_rate
  
		# Calculate amount for delay
		self.amount_for_delay = 0
		self.amount_for_delay_ref = 0
		if self.import_id.date_arrival_port and self.import_id.dispatch_date and self.import_id.route_id:
			days_qty = self.import_id.dispatch_date - self.import_id.date_arrival_port
			days_qty = days_qty.days - self.import_id.route_id.free_days
			for line in self.import_id.shipping_company_id.delay_fee_ids:
				self.amount_for_delay +=  days_qty * line.fee
				self.amount_for_delay_ref +=  days_qty * line.fee_ref
		if self.amount_for_delay < self.import_id.route_id.free_days:
			self.amount_for_delay = 0
			self.amount_for_delay_ref = 0

		#Calculate storage delay
		self.storage_delay = 0
		self.storage_delay_ref = 0
		if self.import_id.empty_return_date and self.import_id.dispatch_date and self.import_id.route_id:
			days_qty = self.import_id.empty_return_date - self.import_id.dispatch_date
			days_qty = days_qty.days - self.import_id.route_id.free_days
			for line in self.import_id.shipping_company_id.delay_fee_ids:
				self.storage_delay +=  days_qty * line.fee
				self.storage_delay_ref +=  days_qty * line.fee_ref
		if self.storage_delay < self.import_id.route_id.free_days:
			self.storage_delay = 0
			self.storage_delay_ref = 0
   
   
		#page products associated (search products in purchase)
		self.forecast_product_ids = [(5,)]
		vals = dict()
		for line in self.import_id.purchase_ids.order_line.filtered(lambda x: x.product_id.detailed_type == 'product').sorted(key=lambda s: s.product_id.id):
			fob = line.currency_id._convert(line.price_unit, self.currency_id, line.company_id, line.date_order)
			fob_ref = line.currency_id._convert(line.price_unit, self.currency_ref_id, line.company_id, line.date_order)
			if vals.get(line.product_id.id, False):
				average += 1
				vals[line.product_id.id][2]['product_qty'] += line.product_qty
				vals[line.product_id.id][2]['fob'] = (vals[line.product_id.id][2]['fob'] + fob)/average
				vals[line.product_id.id][2]['fob_ref'] = (vals[line.product_id.id][2]['fob_ref'] + fob_ref)/average
			else:
				vals[line.product_id.id] = (0, 0, {
					'forecast_id': self.id,
					'product_id': line.product_id.id,
					'product_qty': line.product_qty,
					'product_uom': line.product_uom.id,
					'fob': fob,
					'fob_ref': fob_ref,
				})
				average = 1
		self.forecast_product_ids = list(vals.values())

		#calculations page product associated
		total_qty = sum(self.forecast_product_ids.mapped('product_qty'))
		#Dimensions
		for line in self.forecast_product_ids:
			if self.split_method == 'by_weight':
				line.dimensions = line.product_id.weight * line.product_qty
			elif self.split_method == 'by_volume':
				line.dimensions = line.product_id.volume * line.product_qty
			elif self.split_method == 'by_quantity':
				line.dimensions = total_qty / line.product_qty
			elif self.split_method == 'by_Container':
				capacity = line.product_id.capacities_container_ids.filtered(lambda x: x.id == self.container_type_id.id).total_capacity
				line.dimensions = line.product_qty / capacity if capacity else 0
		
		total_dimensions = sum(self.forecast_product_ids.mapped('dimensions'))
		total_sea_freight_sure = sum(self.associated_expenses_ids.filtered(lambda x: x.concept_type in ['sea_freight','sure']).mapped('fee'))
		total_sea_freight_sure_ref = sum(self.associated_expenses_ids.filtered(lambda x: x.concept_type in ['sea_freight','sure']).mapped('fee_ref'))
		total_land_custom_general_storage = sum(self.associated_expenses_ids.filtered(lambda x: x.concept_type in ['land_freight', 'customs_expenses', 'storage_expenses', 'general_expenses']).mapped('fee'))
		total_land_custom_general_storage_ref = sum(self.associated_expenses_ids.filtered(lambda x: x.concept_type in ['land_freight', 'customs_expenses', 'storage_expenses', 'general_expenses']).mapped('fee_ref'))
		for line in self.forecast_product_ids:
			if self.split_method in ['by_weight', 'by_volume', 'by_quantity']:
				line.cif = (line.dimensions/total_dimensions)*(total_sea_freight_sure/line.product_qty) 
				line.cif_ref = (line.dimensions/total_dimensions)*(total_sea_freight_sure_ref/line.product_qty)
				line.c_national = (line.dimensions/total_dimensions) * (total_land_custom_general_storage/line.product_qty)
				line.c_national_ref = (line.dimensions/total_dimensions) * (total_land_custom_general_storage_ref/line.product_qty)
    
			elif self.split_method == 'by_Container':
				if self.number_container:
					line.cif = ((line.dimensions*self.number_container)/total_dimensions)*(total_sea_freight_sure/line.product_qty) 
					line.cif_ref = ((line.dimensions*self.number_container)/total_dimensions)*(total_sea_freight_sure_ref/line.product_qty)
					line.c_national = ((line.dimensions*self.number_container)/total_dimensions) * (total_land_custom_general_storage/line.product_qty)
					line.c_national_ref = ((line.dimensions*self.number_container)/total_dimensions) * (total_land_custom_general_storage_ref/line.product_qty)
    
			line.in_port = line.fob + line.cif
			line.in_port_ref = line.fob_ref + line.cif_ref
   
			line.in_warehouse = line.in_port + line.c_national
			line.in_warehouse_ref = line.in_port_ref + line.c_national_ref
   
			line.sale_price = (line.in_warehouse*(1+(line.product_id.revenue/100)))
			line.sale_price_ref = (line.in_warehouse_ref*(1+(line.product_id.revenue/100)))
       

	@api.depends('import_id.shipping_company_id', 'import_id.route_id', 'import_id.storage_id')
	def _associated_expenses_ids(self):
		for record in self:
			if record.associated_expenses_ids:
				record.associated_expenses_ids.unlink()
			lines = record.import_id.shipping_company_id.associated_expenses_ids + record.import_id.route_id.associated_expenses_ids + record.import_id.storage_id.associated_expenses_ids
			for line in lines:
				value = False
				value = record.associated_expenses_ids.filtered(lambda x: x.product_id.id == line.product_id.id)
				if not value:
					record.env['ft.associated.expenses'].sudo().create({
						'forecast_id': record.id,
						'product_id' : line.product_id.id,
						'concept_type' : line.concept_type,
						'cost_type' : line.cost_type,
						'fee' : line.fee,
						'fee_ref' : line.fee_ref,
					})
				else:
					value.fee += line.fee
					value.fee_ref += line.fee_ref
