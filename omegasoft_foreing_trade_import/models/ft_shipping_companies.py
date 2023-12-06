# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FtShippingCompanies(models.Model):
    _name = 'ft.shipping.companies'
    _description = 'Shipping companies'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='name',help='Indicates the name of the shipping company.', tracking=True)
    code = fields.Char(string='Reference', help='It is used to establish a reference to the shipping company.', tracking=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('partner_type','in',['supplier', 'customer_supplier'])], 
                                 tracking=True, ondelete='cascade', help="Contact related to the shipping company.")
    
    delay_fee_ids = fields.One2many('ft.delay.fee', 'shipping_company_id', string="Delay fee")
    associated_expenses_ids = fields.One2many('ft.associated.expenses', 'shipping_company_id', string="Associated expenses")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique per company!'),
        ('partner_id', 'unique (partner_id, company_id)', 'This contact is already associated with another shipping company in this company')
    ]
    
    def unlink(self):
        self.delay_fee_ids.unlink()
        self.associated_expenses_ids.unlink()
        return super(FtShippingCompanies, self).unlink()