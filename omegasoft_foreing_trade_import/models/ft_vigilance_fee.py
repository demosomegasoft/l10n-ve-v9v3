# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class FtVigilanceFee(models.Model):
	_name = 'ft.vigilance.fee'
	_description = 'Vigilance fee'
	_order = "tier, id"

	storage_id = fields.Many2one('ft.storage', string="Warehouse", ondelete='restrict')
	tier = fields.Integer(string="Tier", help="Indicates the rate level")
	currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
	currency_ref_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
	fee = fields.Monetary(string="Fee", currency_field='currency_id', help="Indicates the daily amount for delay in the main currency configured")
	fee_ref = fields.Monetary(string="Fee ref", currency_field='currency_ref_id', help="Indicates the daily amount for delay in the configured secondary currency.")
	initial_day = fields.Integer(string="Initial day", help="Start day of the delay period, days off should not be included for this calculation")
	final_day = fields.Integer(string="Final day", help="Day of end of the period due to delay, days off should not be included for this calculation.")
	company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company)

	@api.constrains('initial_day', 'final_day')
	def _constrains_final_day(self):
		for record in self:
			if record.final_day < record.initial_day:
				raise ValidationError(_("The end day cannot be less than the start day"))

	@api.onchange('fee')
	def _onchange_amount(self):
		self.fee_ref = self.currency_id._convert(self.fee, self.currency_ref_id, self.env.company, datetime.now())

	@api.onchange('fee_ref')
	def _onchange_amount_ref(self):
		self.fee = self.currency_ref_id._convert(self.fee_ref, self.currency_id, self.env.company, datetime.now())

	@api.model_create_multi
	def create(self, value_list):
		res = super(FtVigilanceFee, self).create(value_list)
		for record in res:
			record.tier = len(record.storage_id.vigilance_fee_ids.filtered(lambda line: line.tier != 0)) + 1
		return res

	def unlink(self):
		storage_ids = self.storage_id
		res = super(FtVigilanceFee, self).unlink()
		sequence = 1
		for record in storage_ids.vigilance_fee_ids:
			record.tier = sequence
			sequence += 1
		return res