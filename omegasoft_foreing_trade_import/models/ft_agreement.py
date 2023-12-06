# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FtAgreement(models.Model):
    _name = 'ft.agreement'
    _description = 'foreign Trade Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Name',help='In this field the name of the agreement will be established', tracking=True)
    code = fields.Char(string='Reference', help='Indicates the reference that will be used to register the agreement', tracking=True)
    start_date = fields.Date(string='Start Date', help="Indicates the effective date of the agreement")
    end_date = fields.Date(string='End Date', help="Indicates the end date of the agreement's validity")
    line_ids = fields.One2many('ft.agreement.line', 'agreement_id', string="Agreement")
    
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")
    
    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique per company!'),
    ]
    
    @api.constrains('start_date', 'end_date')
    def _constrains_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_("The start date cannot be greater than the end date!"))
    
    #unlink lines
    def unlink(self):
        self.line_ids.unlink()
        return super(FtAgreement, self).unlink()
    
class FtAgreementLine(models.Model):
    _name = 'ft.agreement.line'
    _description = 'foreign Trade Agreement Line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    agreement_id = fields.Many2one('ft.agreement', string="Agreement")
    
    duty_id = fields.Many2one(comodel_name='ft.duty', string='Departure', help='It refers to the tariff item', ondelete='cascade')
    description = fields.Char(related="duty_id.description", readonly=True, help="Indicates the description of the tariff")
    rate = fields.Float(related="duty_id.rate", readonly=True, string="Current rate", help="Indicates the configured duty rate")
    new_rate = fields.Float(string='New rate', help="Establishes the rate that according to the agreement")
    
    _sql_constraints = [
        ('check_new_rate', 'check(new_rate >= 0 and new_rate <= 100)', 'The new rate must be between 0 and 100'),
    ]
    
    @api.model_create_multi
    def create(self, value_list):
        res = super(FtAgreementLine, self).create(value_list)
        for record in res:
            duty_id = record.env['ft.duty'].sudo().search([('id', '=', record.duty_id.id)])
            duty_id.write({'agreement_ids': [(4, record.agreement_id.id, 0)] })
        return res
    
    def unlink(self):
        for record in self:
            duty_id = record.env['ft.duty'].sudo().search([('id', '=', record.duty_id.id)])
            line_agreement = record.agreement_id.line_ids.filtered(lambda x: x.duty_id == record.duty_id)
            if len(line_agreement) == 1:
                duty_id.write({'agreement_ids': [(3, record.agreement_id.id, 0)] })
        return super(FtAgreementLine, self).unlink()
    
    def write(self, vals):
        if vals['duty_id'] and self.duty_id:
            #Elimino la relacion
            duty_id = self.env['ft.duty'].sudo().search([('id', '=', self.duty_id.id)])
            duty_id.write({'agreement_ids': [(3, self.agreement_id.id, 0)] })
            
            #Agregar la nueva relacion
            duty_id = self.env['ft.duty'].sudo().search([('id', '=', vals['duty_id'])])
            duty_id.write({'agreement_ids': [(4, self.agreement_id.id, 0)] })
        return super().write(vals)
        
    