# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class Partner(models.Model):
    _inherit = "res.partner"

    currency_domain_ids = fields.Many2many('res.currency', string='Currency Domain', compute='_compute_currency_domain')

    active_credit = fields.Boolean('Active Credit', help='Activate the credit limit feature', company_dependent=True)
    credit_currency_id = fields.Many2one('res.currency', string='Credit Currency', company_dependent=True)
    amount_limit = fields.Float('Amount Limit', currency_field='credit_currency_id', company_dependent=True)
    credit_total_due = fields.Monetary('Amount Due', currency_field='credit_currency_id', compute='_compute_total_due_overdue')
    credit_total_overdue = fields.Monetary('Amount Overdue', currency_field='credit_currency_id', compute='_compute_total_due_overdue')
    credit_available = fields.Float('Credit Available', currency_field='credit_currency_id', compute='_compute_total_due_overdue')
    sale_invoiceless_amount = fields.Monetary('Sale order invoiceless', currency_field='credit_currency_id', compute='_compute_total_due_overdue')

    @api.depends('active_credit')
    def _compute_currency_domain(self):
        res = self.env.companies.mapped('currency_id')
        res |= self.env.companies.mapped('currency_ref_id')
        self.currency_domain_ids = res

    @api.onchange('active_credit')
    def _onchange_active_credit(self):
        self.credit_currency_id = False

    @api.onchange('credit_currency_id')
    def _onchange_credit_currency_id(self):
        self.amount_limit = 0

    @api.depends('credit_currency_id', 'amount_limit')
    def _compute_total_due_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.id or record._origin:
                if record.env.company.currency_id.id == record.credit_currency_id.id:
                    total_due = record._origin.total_due
                    total_overdue = record._origin.total_overdue
                else:
                    total_due = 0
                    total_overdue = 0
                    for move in record._origin.unpaid_invoice_ids or record.unpaid_invoice_ids:
                        if move.company_id == record.env.company:
                            amount = sum(move.line_ids.mapped('amount_residual_ref'))
                            total_due += amount
                            l = move.line_ids.filtered_domain([('account_id', '=', record.property_account_receivable_id.id)])
                            is_overdue = today > l.date_maturity if l.date_maturity else today > move.date
                            if is_overdue and not l.blocked:
                                total_overdue += amount

                query="""
                    SELECT 
                        pricelist.currency_id,
                        SUM(COALESCE(((sol.product_uom_qty - sol.qty_invoiced) * price_unit) + (((sol.product_uom_qty - sol.qty_invoiced) * price_unit) * (tax.amount/100)), ((sol.product_uom_qty - sol.qty_invoiced) * price_unit)))
                    FROM
                        sale_order
                        JOIN sale_order_line AS sol ON sol.order_id = sale_order.id
                        LEFT JOIN account_tax_sale_order_line_rel AS many_tax ON many_tax.sale_order_line_id = sol.id
                        LEFT JOIN account_tax AS tax ON tax.id = many_tax.account_tax_id
                        LEFT JOIN product_pricelist AS pricelist ON pricelist.id = sale_order.pricelist_id
                    WHERE sale_order.partner_id = {partner_id} 
                        AND sale_order.state IN ('sale', 'done')
                        AND sol.product_uom_qty > sol.qty_invoiced
                        AND sale_order.company_id = {company}
                    GROUP BY 
                        pricelist.currency_id
                """.format(partner_id=record._origin.id, company=record.env.company.id)

                record._cr.execute(query)
                amounts = record._cr.fetchall()
                total_sale_invoiceless = 0

                for amount in amounts:
                    if amount[0] != record.credit_currency_id.id:
                        total_sale_invoiceless += record.env['res.currency'].browse(amount[0])._convert(amount[1], record.credit_currency_id, record.env.company, date.today())
                    else:
                        total_sale_invoiceless += amount[1]


                credit_available = record.amount_limit - total_due - total_sale_invoiceless
                record.sale_invoiceless_amount = total_sale_invoiceless
                record.credit_total_due = total_due
                record.credit_total_overdue = total_overdue
                record.credit_available = credit_available if credit_available > 0 else 0
            else:
                record.sale_invoiceless_amount = 0
                record.credit_total_due = 0
                record.credit_total_overdue = 0
                record.credit_available = 0
