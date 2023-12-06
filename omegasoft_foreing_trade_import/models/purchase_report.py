# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'
    
    concept_type = fields.Selection(
     selection=[
			('sea_freight', 'Sea freight'),
			('land_freight', 'Land freight'),
			('sure', 'Sure'),
			('customs_expenses', 'Customs expenses'),
			('storage_expenses', 'Storage Expenses'),
			('general_expenses', 'General expenses'),
  		], 
    	string="concept type",
    )
    
    cost_type = fields.Selection(
    	selection=[
        	('import', 'Import'),
    		('nationalization', 'Nationalization')
        ],
     	string="cost type",
    )
    
    def _select(self):
        select_str = super()._select()
        select_str += ", t.concept_type as concept_type, t.cost_type as cost_type "
        return select_str
    
    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += """, t.cost_type, t.concept_type """
        return group_by_str
    
    