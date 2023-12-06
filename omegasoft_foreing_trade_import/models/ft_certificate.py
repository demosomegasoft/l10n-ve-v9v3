# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FtCertificate(models.Model):
    _name = "ft.certificate"
    _description = "Certificate"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Name", tracking=True, help="Certificate name")
    code = fields.Char(string="Reference", tracking=True, help="Indicates the reference used to identify the certificate")
    type_id = fields.Many2one('ft.certificate.type', string="Type", tracking=True, ondelete='restrict', help="Sets the type of certificate")
    management_partner_id = fields.Many2one('res.partner', string="Management", tracking=True, help="Contact that manages the certificate")
    init_date = fields.Date(string="From", default=lambda self: datetime.date.today(), tracking=True, help="Initial effective date of the certificate")
    finish_date = fields.Date(string="To", default=lambda self: datetime.date.today() + relativedelta(months=+1), tracking=True, help="End of validity date of the certificate")
    pdf_doc = fields.Binary(string="Document")
    doc_filename = fields.Char(string="Doc Filename", tracking=True, help="Sets the PDF format of the certificate.")
    state = fields.Selection([
        ('current', 'Current'),
        ('to_expire', 'To expire'),
        ('expired', 'Expired')
    ], string="State", compute="_compute_state", help="Indicates the status of the certificate, New, Valid, Expired")
    sequence_state = fields.Integer('Sequence state', compute="_compute_state")
    product_ids = fields.Many2many('product.template', relation='ft_certificate_product_template_rel',  help="Name of the products that require this certificate")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique!'),
    ]

    def _compute_state(self):
        for record in self:
            record.state = "current"
            record.sequence_state = 1
            if record.finish_date:
                current_date = datetime.date.today()
                delta = record.finish_date - current_date
                if delta.days <= 30 and delta.days > 0:
                    record.state = "to_expire"
                    record.sequence_state = 2
                elif delta.days <= 0:
                    record.state = "expired"
                    record.sequence_state = 3

    @api.constrains('init_date', 'finish_date')
    def _validation_date(self):
        for record in self:
            if record.init_date > record.finish_date:
                raise UserError(_("The init date (From) must be less than the finish date (To)."))

    @api.constrains('doc_filename')
    def _doc_filename_validation(self):
        for record in self:
            if record.doc_filename:
                split = record.doc_filename.split('.pdf')
                if len(split) == 1:
                    raise UserError(_("The Document must be a PDF file."))
