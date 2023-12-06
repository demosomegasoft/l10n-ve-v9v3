# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleReport(models.Model):
    _inherit = 'sale.report'
    
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
    
    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['cost_type'] = "t.cost_type"
        res['concept_type'] = "t.concept_type"
        return res
    
    def _group_by_sale(self):
        group_by_str = super()._group_by_sale()
        group_by_str += """, t.cost_type, t.concept_type """
        return group_by_str
    
    