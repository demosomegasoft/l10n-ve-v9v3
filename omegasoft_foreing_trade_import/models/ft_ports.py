# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FtPorts(models.Model):
    _name = 'ft.ports'
    _description = 'foreign Trade Ports'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Name',help='Indicates the name of the port.', tracking=True)
    code = fields.Char(string='Reference', help='Indicates the reference with which the port is established', tracking=True)
    country = fields.Many2one('res.country', help='Indicates the country where the port is located', tracking=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")

    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The reference must be unique per company!'),
        ('name_uniq', 'unique (name, company_id)', 'The name must be unique!')
    ]