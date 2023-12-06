# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FtDuty(models.Model):
    _name = 'ft.duty'
    _description = 'foreign Trade Duty'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Departure',help='Indicates the codification with which the tariff heading is known, example: 4419.11.00.00', tracking=True)
    code = fields.Char(string='Reference', help='It is used to identify by means of a reference to the tariff item.', tracking=True)
    description = fields.Char(string='Description', help="Briefly describe general information about the tariff item")
    rate = fields.Float(string='Rate', help="Indicates the tax rate related to the tariff item.")
    
    line_ids = fields.One2many('ft.duty.line', 'duty_id', string="Duty")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")
        
    agreement_ids = fields.Many2many('ft.agreement', readonly=True, relation='ft_agreement_ft_duty_rel', ondelete='restrict', help="Indicates the name of the associated agreement")
    certificate_type_ids = fields.Many2many('ft.certificate.type', string='Certificate Type', ondelete='restrict', help="Indicates the type of Certificate.")
    
    _sql_constraints = [
        ('check_rate', 'check(rate >= 0 and rate <= 100)', 'The rate must be between 0 and 100'),
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique!'),
        ('name_uniq', 'unique (name, company_id)', 'The name must be unique!')
    ]
    
    def write(self, vals):
        message_upd = ""
        message_new = ""
        message_del = ""
        message = ""
        if 'duty_ids' in vals:
            for line in filter(lambda s: s[0] == 1, vals['duty_ids']):
                message_upd += "<ul>"
                if line[2].get('percentage', False):
                    message_upd += "<li>Porcentaje: %s <span>&#8594;<span/> %s </li>" % (self.duty_ids.browse([line[1]]).percentage, line[2]['percentage'])
                message_upd += "</ul>"
            
            for line in  filter(lambda s: s[0] == 0, vals['duty_ids']):
                message_new += "<ul>"
                if line[2].get('percentage', False):
                    message_new += "<li>Porcentaje: %s </li>" % (line[2]['percentage'])
                message_new += "</ul>"

            for line in  filter(lambda s: s[0] == 2, vals['duty_ids']):
                message_del += "<ul>"
                message_del += "<li>Porcentaje: %s </li>" % (self.duty_ids.browse([line[1]]).percentage)
                message_del += "</ul>"

        if message_upd:
            message += "Porcentaje actualizado:<br/>" + message_upd
        if message_new:
            message += "Porcentaje agregado:<br/>" + message_new
        if message_del:
            message += "Porcentaje eliminado:<br/>" + message_del
            
        res = super().write(vals)
        if message:
            for rec in self:
                rec.message_post(body=message, subtype_xmlid='mail.mt_note')
        return res
    
    def unlink(self):
        self.line_ids.unlink()
        return super(FtDuty, self).unlink()
    
class FtDutyLine(models.Model):
    _name = 'ft.duty.line'
    _description = 'foreign Trade Duty Line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    duty_id = fields.Many2one('ft.duty', string="Duty")
    date_from = fields.Date('Start Date', required=True, help="Indicates the effective date of the exoneration according to the established law.")
    date_to = fields.Date('Stop Date', required=True, help="indicates the expiration date of the exoneration in accordance with the established law.")
    law_agreement = fields.Char('Law agreement', help="Indicates the number of the legal agreement according to the Official Gazette")
    percentage = fields.Float('percentage',tracking=True, help="Indicates the percentage by which the tariff heading will be applied while the exoneration exists.")
    certificate_type_ids = fields.Many2many('ft.certificate.type', string='Certificates', ondelete='restrict', help="Indicates the type of Certificate which will be exonerated.")