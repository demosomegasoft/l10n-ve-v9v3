# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _, exceptions

class FtCertificateType(models.Model):
    _name = "ft.certificate.type"
    _description = "Certificate Type"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Name", tracking=True, help="Indicates the name of the certificate type")
    code = fields.Char(string="Reference", tracking=True, help="Indicates the reference with which the certificate is carried")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique!'),
    ]
    
    certificate_ids = fields.One2many('ft.certificate', 'type_id', string="Certificates")