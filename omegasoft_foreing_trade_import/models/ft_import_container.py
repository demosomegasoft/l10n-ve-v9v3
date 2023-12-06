# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FtImportContainer(models.Model):
	_name = 'ft.import.container'
	_description = 'Import Container'

	import_id = fields.Many2one('ft.import', string="Import", required=True)
	state = fields.Selection(related="import_id.state")
 
	nro_container = fields.Char(string="Nro Container", required=True, 
                            help="Indicates the control number of the container.")
	container_type_id = fields.Many2one('ft.containers', string="Container type", domain=[('active_container', '=', True)], required=True, 
                            help="Indicates the type of registered container.")
 
	def unlink(self):
		if self.state == 'closed_folio':
			raise ValueError(_("the logs of a closed folio cannot be deleted"))
		return super(FtImportContainer, self).unlink()
 