# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	
	is_product_imported = fields.Boolean(string="is product imported", default= False, tracking=True, help="Indicates whether the product is replenished through imports.")
	landed_cost_ok = fields.Boolean(default= False, tracking=True)
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
		tracking=True,
  		# company_dependent=True,
  		help="Indicates the type of service concept this value will be necessary to\n" 
			"establish the costs in imports"
    )
	
	cost_type = fields.Selection(
    	selection=[
        	('import', 'Import'),
    		('nationalization', 'Nationalization')
        ],
     	string="cost type",
    	tracking=True,
		# company_dependent=True,
    	help="Indicates the type of costing that will be established for the service.\n"
     	"Import: Refers to the cost of services acquired abroad that will be allocated to the product.\n" 
      	"Nationalization: Refers to the cost of services purchased in the national territory that will be allocated to the product."
    )
 
	revenue = fields.Float(string="% profit", tracking=True, company_dependent=True, help="Indicates the percentage of profit received by the product for its sale.")
	
	duty_id = fields.Many2one(comodel_name='ft.duty', string="Tariff Item", ondelete='cascade', company_dependent=True, help="Indicates the tariff item number associated with the product")
	description_duty = fields.Char(related="duty_id.description", string="Description duty", readonly=True, help="Indicates the description of the tariff")
	rate_duty = fields.Float(related="duty_id.rate", readonly=True, string="Percentage", help="Indicates the tariff percentage")
	certificate_type_duty_ids = fields.Many2many(related="duty_id.certificate_type_ids", readonly=True, string="Certificate Type", help="Indicates the types of certificates associated with the fee")
	
	#container
	capacities_container_ids = fields.One2many('ft.capacities.container', 'product_id', string="Container Capacities")

 
	capacities_container = fields.Boolean(compute="_compute_capacities_container")
 
	#certificate
	certificate_ids = fields.Many2many('ft.certificate', relation='ft_certificate_product_template_rel', string='Certificate', ondelete='restrict', 
                                       readonly=True, help="")

	
	@api.depends('company_id')
	def _compute_capacities_container(self):
		for rec in self:
			rec.capacities_container = self.env.company.capacities_container

	@api.constrains('revenue')
	def _contrains_revenue(self):
		for record in self:
			if record.revenue < 0 or record.revenue > 100 :
				raise ValidationError(_("The revenue must be between 0 and 100"))
 
	@api.onchange('detailed_type')
	def valid_page_import(self):
		for record in self:
			record.is_product_imported = False
			record.landed_cost_ok = False