# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, Command
from odoo.exceptions import UserError

class CashFlowReport(models.Model):
	_name = "cash.flow.report"
	_description = "Flujo de caja"
	_inherit= ['mail.thread']

	name = fields.Char('Descripción', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
	state = fields.Selection([('draft', 'Borrador'), ('confirmed', 'Confirmado'), ('cancel', 'Cancelado'),], string='Estado', default='draft', tracking=True)
	date_from = fields.Date(string='Desde', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
	date_to = fields.Date(string='Hasta', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
	user_id = fields.Many2one('res.users', string='Responsable', readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
	planned_line_ids = fields.One2many('cash.flow.report.line', 'report_id', string='Lineas planificadas', readonly=True, states={'draft': [('readonly', False)]}, domain=[('planned', '=', True)])
	full_line_ids = fields.One2many('cash.flow.report.line', 'report_id', compute='_compute_full_lines', store=True, string='Lineas', readonly=True)
	summary_journal_line_ids = fields.One2many('cash.flow.report.summary.line', 'report_id', compute='_compute_summary', store=True, domain=[('type', '=', 'journal')])
	summary_partner_line_ids = fields.One2many('cash.flow.report.summary.line', 'report_id', compute='_compute_summary', store=True, domain=[('type', '=', 'partner')])
	planned_total_amount = fields.Monetary(string='Total', currency_field='currency_id', compute='_compute_amount', store=True)
	planned_total_amount_ref = fields.Monetary(string='Total ref', currency_field='currency_ref_id', compute='_compute_amount', store=True)
	currency_id = fields.Many2one(related='company_id.currency_id', store=True)
	currency_ref_id = fields.Many2one(related='company_id.currency_ref_id', store=True)
	company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company.id, readonly=True, required=True)

	@api.depends('planned_line_ids.expected_amount', 'planned_line_ids.expected_amount_ref')
	def _compute_amount(self):
		for report in self:
			planned_total_amount = planned_total_amount_ref = 0.0
			for line in report.planned_line_ids:
				planned_total_amount += line.expected_amount
				planned_total_amount_ref += line.expected_amount_ref
			report.planned_total_amount = planned_total_amount
			report.planned_total_amount_ref = planned_total_amount_ref

	@api.depends('state')
	def _compute_full_lines(self):
		for report in self:
			not_planned_lines = report.full_line_ids.filtered(lambda l: not l.planned)
			if report.state != 'confirmed' and not_planned_lines:
				not_planned_lines.unlink()

	@api.depends('full_line_ids.journal_id', 'full_line_ids.partner_id')
	def _compute_summary(self):
		for report in self:
			by_journal = defaultdict(list)
			by_partner = defaultdict(list)
			for line in report.full_line_ids:
				by_journal[line.journal_id.id].append(line.id)
				by_partner[line.partner_id.id].append(line.id)
			report.summary_journal_line_ids = [Command.clear()] + [Command.create({'type': 'journal', 'journal_id': k, 'full_line_ids': [Command.set(v)]}) for k, v in by_journal.items()]
			report.summary_partner_line_ids = [Command.clear()] + [Command.create({'type': 'partner', 'partner_id': k, 'full_line_ids': [Command.set(v)]}) for k, v in by_partner.items()]

	def button_update(self):
		invoices = self.full_line_ids.mapped(lambda l: (l.invoice_id.id, l.journal_id.id))
		payment_ids = self.env['account.payment'].search([
			('payment_type', '=', 'inbound'),
			('state', '=', 'posted'),
			('date', '>=', self.date_from),
			('date', '<=', self.date_to),
			('company_id', '=', self.company_id.id)
		])
		for payment in payment_ids:
			for invoice in payment.reconciled_invoice_ids:
				invoice_journal = (invoice.id, payment.journal_id.id)
				if invoice_journal not in invoices:
					invoices.append(invoice_journal)
					self.env['cash.flow.report.line'].create({
						'planned': False,
						'report_id': self.id,
						'invoice_id': invoice.id,
						'journal_id': payment.journal_id.id,
					})

	def add_invoices(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Facturas',
			'res_model': 'account.move',
			'view_mode': 'tree',
			'view_id': self.env.ref('omegasoft_sale_cash_flow.select_invoices_tree_view').id,
			'target': 'new',
			'domain': [
				('id', 'not in', self.planned_line_ids.invoice_id.ids),
				('move_type', '=', 'out_invoice'),
				('state','=','posted'),
				('amount_residual', '!=', 0),
				('date', '>=', self.date_from),
				('date', '<=', self.date_to),
				('company_id', '=', self.company_id.id),
			],
		}

	def button_draft(self):
		self.write({'state': 'draft'})

	def button_confirm(self):
		self.write({'state': 'confirmed'})

	def button_cancel(self):
		self.write({'state': 'cancel'})

	def unlink(self):
		for report in self:
			if report.state != 'cancel':
				raise UserError('Solo puedes suprimir registros en estado cancelado !')
		return super().unlink()


class CashFlowReportLine(models.Model):
	_name = "cash.flow.report.line"
	_description = "Lineas de flujo de caja"

	planned = fields.Boolean(default=False)
	report_id = fields.Many2one('cash.flow.report', required=True, ondelete='cascade')
	invoice_id = fields.Many2one('account.move', string='Numero de factura', required=True, readonly=True)
	partner_id = fields.Many2one(related='invoice_id.partner_id', string='Cliente')
	invoice_date_due = fields.Date(related='invoice_id.invoice_date_due', string='Fecha de vencimiento')
	invoice_currency_id = fields.Many2one(related='invoice_id.currency_id')
	amount_residual = fields.Monetary(related='invoice_id.amount_residual', string='Monto adeudado', currency_field='invoice_currency_id')
	journal_id = fields.Many2one('account.journal', string='Diario de banco o caja', domain=[('type', 'in', ('bank', 'cash'))])
	journal_currency_id = fields.Many2one('res.currency', string='Moneda de diario', compute='_compute_journal_currency_id')
	date = fields.Date(string='Fecha')
	date_from = fields.Date(related='report_id.date_from')
	date_to = fields.Date(related='report_id.date_to')
	expected_amount = fields.Monetary(string='Monto esperado', default=0, currency_field='currency_id')
	expected_amount_ref = fields.Monetary(string='Monto esperado Ref', default=0, currency_field='currency_ref_id')
	received_amount = fields.Monetary(string='Importe real', compute='_compute_received', store=True, currency_field='currency_id')
	received_amount_ref = fields.Monetary(string='Importe real Ref', compute='_compute_received', store=True, currency_field='currency_ref_id')
	currency_id = fields.Many2one(related='report_id.currency_id', store=True)
	currency_ref_id = fields.Many2one(related='report_id.currency_ref_id', store=True)
	company_id = fields.Many2one(related='report_id.company_id', store=True)
	achievement = fields.Float('Logro', compute='_compute_received', store=True)

	@api.depends('journal_id')
	def _compute_journal_currency_id(self):
		for line in self:
			line.journal_currency_id = line.journal_id.currency_id.id or line.currency_id.id

	@api.depends('report_id.state', 'invoice_id.line_ids.matched_credit_ids.amount', 'invoice_id.line_ids.matched_credit_ids.amount_ref')
	def _compute_received(self):
		for line in self:
			if line.report_id.state == 'confirmed':
				matched_credit_ids = line.invoice_id.line_ids.filtered(lambda l: l.account_type == 'asset_receivable').matched_credit_ids.filtered(
					lambda m: m.credit_move_id.date >= line.date_from and m.credit_move_id.date <= line.date_to and m.credit_move_id.journal_id.id == line.journal_id.id
				)
				line.received_amount = sum(matched_credit_ids.mapped('amount'))
				line.received_amount_ref = sum(matched_credit_ids.mapped('amount_ref'))
				line.achievement = line.expected_amount > 0 and line.received_amount / line.expected_amount or 0.0
			else:
				line.received_amount = 0.0
				line.received_amount_ref = 0.0
				line.achievement = 0.0


class CashFlowReportLine(models.Model):
	_name = "cash.flow.report.summary.line"
	_description = "Lineas resumen de flujo de caja"

	report_id = fields.Many2one('cash.flow.report', required=True, ondelete='cascade')
	type = fields.Selection([('journal', ''), ('partner', '')], string='Tipo', required=True)
	full_line_ids = fields.Many2many('cash.flow.report.line', string='Lineas planificadas')
	partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
	journal_id = fields.Many2one('account.journal', string='Diario de banco o caja', domain=[('type', 'in', ('bank', 'cash'))])
	date_from = fields.Date(related='report_id.date_from')
	date_to = fields.Date(related='report_id.date_to')
	expected_amount = fields.Monetary(string='Monto esperado', compute='_compute_amount', store=True, currency_field='currency_id')
	expected_amount_ref = fields.Monetary(string='Monto esperado Ref', compute='_compute_amount', store=True, currency_field='currency_ref_id')
	received_amount = fields.Monetary(string='Importe real', compute='_compute_amount', store=True, currency_field='currency_id')
	received_amount_ref = fields.Monetary(string='Importe real Ref', compute='_compute_amount', store=True, currency_field='currency_ref_id')
	currency_id = fields.Many2one(related='report_id.currency_id')
	currency_ref_id = fields.Many2one(related='report_id.currency_ref_id')
	company_id = fields.Many2one(related='report_id.company_id')
	achievement = fields.Float('Logro', compute='_compute_amount', store=True)

	@api.depends(
		'full_line_ids.expected_amount',
		'full_line_ids.expected_amount_ref',
		'full_line_ids.received_amount',
		'full_line_ids.received_amount_ref'
	)
	def _compute_amount(self):
		for line in self:
			expected_amount = expected_amount_ref = 0.0
			received_amount = received_amount_ref = 0.0
			for cash_line in line.full_line_ids:
				expected_amount += cash_line.expected_amount
				expected_amount_ref += cash_line.expected_amount_ref
				received_amount += cash_line.received_amount
				received_amount_ref += cash_line.received_amount_ref
			line.expected_amount = expected_amount
			line.expected_amount_ref = expected_amount_ref
			line.received_amount = received_amount
			line.received_amount_ref = received_amount_ref
			line.achievement = expected_amount > 0 and received_amount / expected_amount or 0.0