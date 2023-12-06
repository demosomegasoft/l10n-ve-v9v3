# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FtForecast(models.Model):
	_name = 'ft.forecast.product'
	_description = 'Import foreign trade forecast product associated with purchase'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
	_order = 'forecast_id desc'

	forecast_id = fields.Many2one('ft.forecast', string="Forecast")
	import_id = fields.Many2one(related="forecast_id.import_id", string="Import")
	purchase_ids = fields.One2many(related="import_id.purchase_ids", string="Purchase")

	
	#products associated with purchase
	currency_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
	currency_ref_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
	product_id = fields.Many2one('product.product', string="Product", readonly=True)
	product_qty = fields.Float(string="Quantity", readonly=True)
	product_uom = fields.Many2one('uom.uom', string="UdM", readonly=True)
	dimensions = fields.Float(string="Dimensions", readonly=True)
	fob = fields.Monetary(string="Unit price", currency_field='currency_id', readonly=True)
	fob_ref = fields.Monetary(string="Unit price ref", currency_field='currency_ref_id', readonly=True)
	cif = fields.Monetary(string="CIF", currency_field='currency_id', readonly=True)
	cif_ref = fields.Monetary(string="CIF ref", currency_field='currency_ref_id', readonly=True)
	in_port = fields.Monetary(string="In port", currency_field='currency_id', readonly=True)
	in_port_ref = fields.Monetary(string="In port ref", currency_field='currency_ref_id', readonly=True)
	c_national = fields.Monetary(string="C.National", currency_field='currency_id', readonly=True)
	c_national_ref = fields.Monetary(string="C.National ref", currency_field='currency_ref_id', readonly=True)
	in_warehouse = fields.Monetary(string="In warehouse", currency_field='currency_id', readonly=True)
	in_warehouse_ref = fields.Monetary(string="In warehouse ref", currency_field='currency_ref_id', readonly=True)
	sale_price = fields.Monetary(string="Sale price", currency_field='currency_id', readonly=True)
	sale_price_ref = fields.Monetary(string="Sale price ref", currency_field='currency_ref_id', readonly=True)