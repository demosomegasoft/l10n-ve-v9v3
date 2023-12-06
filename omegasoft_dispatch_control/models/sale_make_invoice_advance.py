# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if res:
            dispatch = self.env['dispatch.control'].create(
                {
                    'invoice_id': res.id,
                    'sale_order_id': self._context.get('active_id', False),
                }
            )
            if dispatch:
                res.dispatch_control_id = dispatch
        return res
