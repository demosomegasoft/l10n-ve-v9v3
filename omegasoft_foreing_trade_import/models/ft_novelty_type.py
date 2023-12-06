# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FtNovltyType(models.Model):
    _name = 'ft.novelty.type'
    _description = 'Types of novelty'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Name", tracking=True, required=True, help="Indicates the name of the certificate type")
    code = fields.Char(string="Reference", tracking=True, help="Indicates the reference with which the certificate is carried")
    description = fields.Char(string="Default Description", tracking=True, help="It serves to briefly describe what happens when the novelty occurs in the import process")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", help="Company", default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.", tracking=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique for company!')
    ]