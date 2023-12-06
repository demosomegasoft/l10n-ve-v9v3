# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    dispatch_control_id = fields.Many2one('dispatch.control', string="Dispatch Control", readonly=True, ondelete='restrict')