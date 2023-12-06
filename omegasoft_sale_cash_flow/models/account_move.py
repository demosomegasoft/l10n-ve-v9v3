# -*- coding: utf-8 -*-

from odoo import models

class AccountMove(models.Model):
	_inherit = "account.move"

	def add_invoices(self):
		report_id = self._context.get('active_id')
		self.env['cash.flow.report.line'].create([{
			'planned': True,
			'report_id': report_id,
			'invoice_id': invoice_id.id,
			'expected_amount': invoice_id.amount_residual_signed,
			'expected_amount_ref': sum(invoice_id.line_ids.filtered(lambda l: l.account_type == 'asset_receivable').mapped('amount_residual_ref')),
		} for invoice_id in self])