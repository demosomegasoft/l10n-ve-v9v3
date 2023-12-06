# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped, final, date)
        for rec in res:
            dispatch = self.env['dispatch.control'].create(
                {
                    'invoice_id': rec.id,
                    'sale_order_id': self._context.get('active_id', False) or self.id,
                }
            )
            if dispatch:
                rec.dispatch_control_id = dispatch
        return res