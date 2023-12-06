# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FtStorage(models.Model):
	_name = 'ft.storage'
	_description = 'Ft Storage'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

	name = fields.Char(string='Name', tracking=True, required=True, help="Indicates the name of the store")
	code = fields.Char(string='Reference', tracking=True, required=True, help="Establishes the reference by which the store is known")
	company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company)
	active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")

	#delay fee
	delay_fee_ids = fields.One2many('ft.delay.fee', 'storage_id', string="Delay fee")
	# vigilance payment fee 
	vigilance_fee_ids = fields.One2many('ft.vigilance.fee', 'storage_id', string="Vigilance fee")
	# associated expenses
	associated_expenses_ids = fields.One2many('ft.associated.expenses', 'storage_id', string="Associated expenses")

	_sql_constraints = [
		('code_uniq', 'unique (code,company_id)', 'The code must be unique!')
	]
 
	#unlink lines
	def unlink(self):
		self.delay_fee_ids.unlink()
		self.vigilance_fee_ids.unlink()
		self.associated_expenses_ids.unlink()
		return super(FtStorage, self).unlink()