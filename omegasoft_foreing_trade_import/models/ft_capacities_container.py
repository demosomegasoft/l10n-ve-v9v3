# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FtCapacitiesContainer(models.Model):
	_name = 'ft.capacities.container'
	_description = 'Foreign Trade capacities container'
	_rec_name = "container_id"
 
	#container

	product_id = fields.Many2one('product.template', 'Product')
	container_id = fields.Many2one('ft.containers', string="Container", domain=[('active_container', '=', True)], 
                            help="Indicates the name of the container")
	active_container = fields.Boolean(related="container_id.active_container")
	total_capacity = fields.Float(string="Total capacity", 
                            help="It establishes the maximum quantity of products that can be loaded in the container, based on this calculation, automated estimates can be made in imports to quickly establish the containers that will be necessary.")

	_sql_constraints = [
		('code_uniq', 'unique (product_id,container_id)', 'The Container must be unique per product!')
	]