# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

APPROVAL_STATES = [
    ('not_approved', 'Not Approved'),
    ('to_approve', 'To Approve'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('canceled', 'Canceled'),
]

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    active_credit = fields.Boolean('Active Credit', related='partner_id.active_credit')
    credit_currency_id = fields.Many2one('res.currency', string='Credit Currency', related='partner_id.credit_currency_id')

    amount_limit = fields.Float('Amount Limit', currency_field='credit_currency_id', related='partner_id.amount_limit')
    credit_total_due = fields.Monetary('Amount Due', currency_field='credit_currency_id',related='partner_id.credit_total_due')
    credit_total_overdue = fields.Monetary('Amount Overdue', currency_field='credit_currency_id',related='partner_id.credit_total_overdue')
    credit_available = fields.Float('Credit Available', currency_field='credit_currency_id',related='partner_id.credit_available')
    sale_invoiceless_amount = fields.Monetary('Sale order invoiceless', currency_field='credit_currency_id',related='partner_id.sale_invoiceless_amount')

    limit_exceeded = fields.Boolean('Limit Exceeded', compute='_compute_limit_exceeded')
    exceeded_amount = fields.Monetary('Exceeded amount', currency_field='credit_currency_id', compute='_compute_limit_exceeded')

    approval_state = fields.Selection(
        APPROVAL_STATES,
        string = 'Status',
        default = 'not_approved',
        required = True,
        index = True,
        copy = False,
        tracking=True,
    )
    order_amount = fields.Float(compute='_compute_order_amount', string='Order Amount')
    
    @api.depends('state')
    def _compute_order_amount(self):
        for rec in self:
            if rec.state == 'sale':
                query="""
                    SELECT 
                        amount_total
                    FROM
                        sale_order
                    WHERE
                        id = {id}
                """.format(id=rec._origin.id or rec.id)
                rec._cr.execute(query)
                result = rec._cr.fetchone()
                amount = result[0]
                if rec.partner_id.credit_currency_id != rec.pricelist_id.currency_id:
                    amount = rec.pricelist_id.currency_id._convert(amount, rec.partner_id.credit_currency_id, rec.company_id, rec.date_order)
                rec.order_amount = amount
            else:
                rec.order_amount = 0

    @api.depends('tax_totals')
    def _compute_limit_exceeded(self):
        for rec in self:
            record = rec._origin or rec
            amount_total = rec.tax_totals['amount_total']
            if record.partner_id.credit_currency_id != record.pricelist_id.currency_id:
                amount_total = record.pricelist_id.currency_id._convert(amount_total, record.partner_id.credit_currency_id, record.company_id, record.date_order)

            exceeded_amount = (record.credit_available - amount_total) + rec.order_amount
            if exceeded_amount < 0 and not float_is_zero(exceeded_amount, 2) and record.active_credit:
                rec.limit_exceeded = True
                rec.exceeded_amount = abs(exceeded_amount)
            else:
                rec.limit_exceeded = False
                rec.exceeded_amount = 0

    def action_request_for_approval(self):
        if self.approval_state and self.approval_state not in ['not_approved', 'rejected']:
            return

        # Next approval_states: approved, rejected, canceled
        self.approval_state = 'to_approve'


    def action_approve_sale_order(self):
        if self.approval_state != 'to_approve':
            return

        # Next approval_states: cancelled
        self.approval_state = 'approved'
        return self.with_context(validate_analytic = True).action_confirm()


    def action_reject_sale_order(self):
        if self.approval_state != 'to_approve':
            return

        # Next approval_states: not_approved
        self.approval_state = 'rejected'


    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()

        # Next approval_states: not_approved
        self.approval_state = 'canceled'
        return result


    def action_draft(self):
        result = super(SaleOrder, self).action_draft()

        # Next approval_states: to_approve
        self.approval_state = 'not_approved'
        return result
