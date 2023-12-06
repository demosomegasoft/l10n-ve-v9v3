# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FtBinnacle(models.Model):
	_name = 'ft.binnacle'
	_description = 'Import foreign trade binnacle'
	_order = 'date desc'

	import_id = fields.Many2one('ft.import', string="Import", required=True)
	state = fields.Selection(related="import_id.state")
	novelty_type_id = fields.Many2one('ft.novelty.type', string="Novelty", required=True, 
                                   help="Indicates the type of novelty.")
	date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True, 
                        help="Indicates the date on which the novelty was registered.")
	description = fields.Char(related="novelty_type_id.description", string="Description", readonly=False, 
                           help="It is used to generically describe a summary of the novelty.")
	user_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user, readonly=True,
                           help="Indicates the user who generated the record.")