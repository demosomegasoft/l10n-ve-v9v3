# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from random import randint


class ImportLabels(models.Model):
    _name = 'ft.label'
    _description = 'Foreign Trade Labels'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name', required=True, help='Indicates the name of the label')
    color = fields.Integer(string='Color index',help='Color index', default=_get_default_color)
    code = fields.Char(string='Code' , help='Set a unique code for the tag')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")

    _sql_constraints = [
        ('code_uniq', 'unique (code,company_id)', 'The code must be unique per company!')
    ]