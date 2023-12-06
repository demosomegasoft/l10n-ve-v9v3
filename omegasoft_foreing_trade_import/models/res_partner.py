# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Partner(models.Model):
	_inherit = "res.partner"

	customs_agent = fields.Boolean(string="Customs agent", default=False,
                                help="Through this button, the contact is configured as a customs agent so that it can be selected in an import process")
 
	exporter_agent = fields.Boolean(string="Exporter agent", default=False,
                                help="Indicates that the supplier is related to an import purchase process.")