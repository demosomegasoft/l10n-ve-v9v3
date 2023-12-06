# coding: utf-8

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	
	#domains in fields and view
	person_type_code = fields.Char(related='partner_id.person_type_code')

	#ft_import
	import_id = fields.Many2one('ft.import', string="Import file number", domain=[('state', '!=', 'closed_folio')])
	state_impor_id = fields.Selection(related="import_id.state")
 
	#container
	capacities_container = fields.Boolean(related='company_id.capacities_container')
	container_id = fields.Many2one('ft.containers', string="Container type", domain=[('active_container', '=', True)], 
                            help="Sets the type of container with which the import is expected to be handled")
	exporter_agent = fields.Boolean(related='partner_id.exporter_agent')	
	products_with_issues = fields.Many2many('product.product', string="Products with Issues", compute="_compute_active_notification", store=True)


	measurement = fields.Selection([
        ('vol', 'Volume'),
        ('weight', 'Weight'),
        ('qty', 'Quantity per container'),
    ], string='Measurement',
        help="Indicates the extent to which the estimation of the containers required in the import process was made")
 
	recommended_containers = fields.Float('No. of containers', compute='_compute_total_container',
                                       help="Indicates the number of containers recommended to import the products.")

	@api.depends('order_line.container_qty')
	def _compute_total_container(self):
		for rec in self:
			rec.recommended_containers = sum(rec.order_line.mapped('container_qty'))
   
	@api.onchange('container_id')
	def _onchange_valid_container_id(self):
		if self.container_id and not (self.container_id.maximum_load and self.container_id.cubic_capacity):
			raise UserError(_("Cannot make estimates if container config is not set to:\n"
								"Maximum load\n"
								"Cubicage"))

	@api.onchange('measurement')
	def _onchange_reset_container_id(self):
		if self.container_id:
			self.container_id = False
   
	@api.depends('order_line', 'order_line.write_date')
	def _compute_active_notification(self):
		for order in self:
			products_with_issues = self.env['product.product']
			for line in order.order_line:
				if line.company_id.capacities_container and line.order_id.container_id:
					if line.measurement == 'weight' and not line.product_id.weight:
						products_with_issues |= line.product_id
					elif line.measurement == 'vol' and not line.product_id.volume:
						products_with_issues |= line.product_id
					elif line.measurement == 'qty' and not line.product_id.capacities_container_ids.filtered(lambda cont: cont.container_id.id == line.order_id.container_id.id).total_capacity:
						products_with_issues |= line.product_id
			order.products_with_issues = [(6, 0, products_with_issues.ids)]

    
	def _prepare_invoice(self):
		res = super(PurchaseOrder, self)._prepare_invoice()
		if self.import_id:
			res['import_id'] = self.import_id.id
			res['importation_process'] = True
		return res

from odoo import models, fields

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'
 
	container_qty = fields.Float(string='Ability', compute='_compute_container_qty',
                              help="Indicates the capacity of the purchased products related to the type of container selected and its measurement.")
	measurement = fields.Selection(related='order_id.measurement')
	capacities_container = fields.Boolean(related='order_id.capacities_container')
	person_type_code = fields.Char(related='order_id.person_type_code') 
	#Certificare bottom

	certificate_danger_alert = fields.Boolean(compute="_compute_certificate_alert")
	certificate_warning_alert = fields.Boolean(compute="_compute_certificate_alert")
	certificate_success_alert = fields.Boolean(compute="_compute_certificate_alert")
	certificate_muted_alert = fields.Boolean(compute="_compute_certificate_alert")

	@api.depends('product_id')
	def _compute_certificate_alert(self):
		for rec in self:
			if rec.person_type_code == 'PJND' or rec.person_type_code == 'PNNR':
				if self.product_certificate_success_alert(rec.product_id):
					rec.certificate_danger_alert = False
					rec.certificate_warning_alert = False
					rec.certificate_success_alert = True
					rec.certificate_muted_alert = False
     
				elif self.product_certificate_warning_alert(rec.product_id):
					rec.certificate_danger_alert = False
					rec.certificate_warning_alert = True
					rec.certificate_success_alert = False
					rec.certificate_muted_alert = False
     
				elif self.product_certificate_danger_alert(rec.product_id):
					rec.certificate_danger_alert = True
					rec.certificate_warning_alert = False
					rec.certificate_success_alert = False
					rec.certificate_muted_alert = False
     
				else: #muted
					rec.certificate_danger_alert = False
					rec.certificate_warning_alert = False
					rec.certificate_success_alert = False
					rec.certificate_muted_alert = True
     
			else:
				rec.certificate_danger_alert = False
				rec.certificate_warning_alert = False
				rec.certificate_success_alert = False
				rec.certificate_muted_alert = False
 
	def button_pass(self):
		pass
	
	def product_certificate_success_alert(self, product):
		if any(certificate.state == 'current' for certificate in product.mapped('certificate_ids')):
			return True
	
	def product_certificate_warning_alert(self,product):
		if any(certificate.state == 'to_expire' for certificate in product.mapped('certificate_ids')):
			return True

	def product_certificate_danger_alert(self,product):
		if any(certificate.state == 'expired' for certificate in product.mapped('certificate_ids')):
			return True


	@api.depends('product_qty', 'product_id', 'order_id.container_id')
	def _compute_container_qty(self):
		for rec in self:
			if rec.company_id.capacities_container:
				if rec.measurement == 'weight':
					rec.container_qty = (rec.product_id.weight * rec.product_qty) / rec.order_id.container_id.maximum_load if rec.order_id.container_id.maximum_load else 0
				
				elif rec.measurement == 'vol':
					rec.container_qty = (rec.product_id.volume * rec.product_qty) / rec.order_id.container_id.cubic_capacity if rec.order_id.container_id.cubic_capacity else 0					
   				
				elif rec.measurement == 'qty':
					value = rec.product_id.capacities_container_ids.filtered(lambda line: line.container_id.id == rec.order_id.container_id.id).total_capacity
					rec.container_qty = rec.product_qty / value if value else 0
				else:
					rec.container_qty = 0
			else:
				rec.container_qty = 0

