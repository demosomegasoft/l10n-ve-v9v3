# coding: utf-8
from odoo import models, fields, api, _

class AccountMove(models.Model):
	_inherit = 'account.move'
	
	import_id = fields.Many2one('ft.import', string="Import file number", domain=[('state', '!=', 'closed_folio')],
                             help="Indicates the number of the import file managed")
	partner_type = fields.Selection(related='partner_id.partner_type')
	person_type_code = fields.Char(related='partner_id.person_type_code')
	
	importation_process = fields.Boolean(string="Importation process", default=False)

	@api.onchange('partner_id', 'importation_process')
	def _onchange_import_partner(self):
		if self.move_type in ['in_refund', 'in_invoice'] and self.person_type_code == 'PJND' and self.partner_type in ['supplier', 'customer_supplier']:
			self.importation_process = True