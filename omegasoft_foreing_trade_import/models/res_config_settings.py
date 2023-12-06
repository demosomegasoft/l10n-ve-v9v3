from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    #Novelty
    group_ft_novelty = fields.Boolean(string="Novelty type", implied_group='omegasoft_foreing_trade_import.group_ft_novelty')    
    
    #Container
    capacities_container = fields.Boolean(related='company_id.capacities_container', string="Capacities per Container", readonly=False, required=True,
                                        help="It allows to establish the measurement by containers in the calculations of the cost structure of products." )
    
    #tax
    import_purchase_tax = fields.Many2one(related='company_id.import_purchase_tax', string='Default Purchase Tax', readonly=False,
                                          help="The tax that will be used to calculate the forecast tab and the taxes related to imports must be established.")
    