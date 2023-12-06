# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import calendar


class SalesGoalLine(models.Model):
    _name = 'sales.goal.line'
    _description = 'Sales Goal Line'

    sales_goal_id = fields.Many2one('sales.goal', string="Sales goal", ondelete="restrict")
    sales_goal_start_date = fields.Date(related='sales_goal_id.start_date', store=True)
    sales_goal_end_date = fields.Date(related='sales_goal_id.end_date', store=True)
    user_id = fields.Many2one('res.users', string="Sales person", ondelete="restrict", required=True)
    company_id = fields.Many2one(related='sales_goal_id.company_id')
    goal = fields.Monetary(string="Goal", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
    accumulated_goal = fields.Monetary(string="Accumulated goal", readonly=True)
    percentage = fields.Float(string="Percentage", readonly=True)
    compute_accumulated_goal = fields.Boolean(compute="_compute_accumulated_goal")

    @api.onchange('user_id')
    def _onchange_user_id(self):
        user_ids = self.sales_goal_id.line_ids.mapped('user_id')
        return {'domain': {'user_id': [('id', 'not in', user_ids.ids)]}}

    def unlink(self):
        for rec in self:
            if rec.percentage > 0:
                raise ValidationError(_('You cannot delete a line with related invoices.'))
        return super(SalesGoalLine, self).unlink()

    @api.onchange('goal')
    def _onchange_goal(self):
        if self.goal < 0:
            raise ValidationError(_('You cannot enter negative numbers.'))
        elif self.percentage != 0:
            self.percentage = (self.accumulated_goal * 100) / self.goal

    @api.constrains('goal')
    def _constrains_goal(self):
        for rec in self:
            if rec.goal <= 0:
                raise ValidationError(_("The goal can't be cero, please set a diferente value."))

    def _compute_accumulated_goal(self):
        self._calculate_accumulated_goal()
        self.compute_accumulated_goal = True

    def _calculate_accumulated_goal(self):
        for rec in self:
            invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('user_id', '=', rec.user_id.id), ('invoice_date', '>=', rec.sales_goal_start_date), ('invoice_date', '<=', rec.sales_goal_end_date), ('company_id', '=', rec.company_id.id)])
            rec.accumulated_goal = sum([invoice.currency_id._convert(invoice.amount_untaxed, rec.currency_id, invoice.company_id, invoice.invoice_date) for invoice in invoices])
            rec.percentage = (rec.accumulated_goal * 100) / rec.goal