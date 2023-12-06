# coding: utf-8
from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    type_tax_use = fields.Selection(selection_add=[
        ('tsa', 'Customs Service Rate'),
        ('tss', 'Seniat Rate'),
    ], ondelete={'tsa': 'set default',
                 'tss': 'set default'})
    
    delete_tax = fields.Boolean(default=False, groups="omegasoft_foreing_trade_import.group_admin_imports")
    
    def unlink(self):
        for record in self:
            if record.delete_tax:
                raise UserError(_("the tax: %s cannot be removed from the model, it can only be archived", record.name))
        return super(AccountTax, self).unlink()
    
     
    
