# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class FtImportRoutes(models.Model):
    _name = 'ft.import.routes'
    _description = 'Import stages'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Name', tracking=True, required=True, help='route name')
    code = fields.Char(string='Reference', tracking=True, required=True, 
                       help='Unique code with which the route can be easily recognized.')
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 help='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")

    origin_routes = fields.Many2one('ft.ports', string="Origin routes", ondelete="restrict", tracking=True, required=True, 
                                    help='indicates the original port of shipment of the merchandise')
    intermediate_1 = fields.Many2one('ft.ports', string="Intermediate 1", ondelete="restrict", tracking=True, 
                                     help='Indicates if the shipping company has 1 or more stops before reaching the port of destination.')
    intermediate_2 = fields.Many2one('ft.ports', string="Intermediate 2", ondelete="restrict", tracking=True, 
                                     help='Indicates if the shipping company has 1 or more stops before reaching the port of destination.')
    intermediate_3 = fields.Many2one('ft.ports', string="Intermediate 3", ondelete="restrict", tracking=True, 
                                     help='Indicates if the shipping company has 1 or more stops before reaching the port of destination.')
    destination_id = fields.Many2one('ft.ports', string="Destination", ondelete="restrict", tracking=True, 
                                  help='Indicates the final port of destination')

    estimated_traffic = fields.Float(string="Estimated traffic", tracking=True, 
                                     help='It indicates the estimated value based on the experience of time that the merchandise requires to arrive at the port, this value is an empirical calculation.')
    real_transit = fields.Float(string="Real transit", compute="_compute_real_transit",
                                help='Indicates the real-time calculation of the transit of merchandise in the import process based on previously registered imports')
    shipping_company_id = fields.Many2one('ft.shipping.companies', string="Shipping company", ondelete="restrict", tracking=True, 
                                          help='Indicates the name of the shipping company with which you work on the route.')
    free_days = fields.Integer(string="Free days", tracking=True, 
                               help='Indicates the free days that are negotiated by the shipping company in the import route.')
    currency_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
    currency_ref_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
    freight_price = fields.Monetary(string="Freight price", currency_field='currency_id', compute="_compute_freight_prices", tracking=True,
                                    help='Indicates the freight price in the main currency.')
    freight_price_ref = fields.Monetary(string="Freight price ref", currency_field='currency_ref_id', compute="_compute_freight_prices", tracking=True,
                                        help='Indicates the freight price in Ref currency')
    freight_concept_id = fields.Many2one('product.template', string='Freight Concept', required=True, tracking=True, domain=[('detailed_type', '=', 'service'),('landed_cost_ok', '=', 'True'),('concept_type', '=', 'sea_freight')],
                                         help='Establishes the associated freight product so that calculation estimates can be made in the import model')
    state = fields.Selection(selection=[('active', 'Active'),('inactive', 'Inactive'),], string='Status', 
                            tracking=True, default='active',)
    # Associated expenses
    associated_expenses_ids = fields.One2many('ft.associated.expenses', 'route_id', string="Associated expenses")

    #Freight Rates
    freight_rate_ids = fields.One2many('ft.import.routes.freight.rates', 'route_id', string='Freight Rates')

    _sql_constraints = [
        ('code_uniq', 'unique (code,company_id)', 'The code must be unique!')
    ]
    
    @api.constrains('freight_concept_id', 'associated_expenses_ids')
    def _contrains_validation(self):
        for record in self:
            if record.freight_concept_id:
                freight_concept_line = record.associated_expenses_ids.filtered(lambda l: l.product_id.id == record.freight_concept_id.id)
                if not freight_concept_line:
                    raise ValidationError(_("There must be at least one line related to the freight concept in the associated expenses tab"))
                
    @api.onchange('freight_concept_id')
    def _onchange_freight_concept_id(self):
        for record in self:
            if record.freight_concept_id:
                freight_concept_line = record.associated_expenses_ids.filtered(lambda l: l.product_id.id == record.freight_concept_id.id)
                if not freight_concept_line:
                    self.env['ft.associated.expenses'].create({
                        'product_id': record.freight_concept_id.id,
                        'route_id': record.id,
                        'concept_type': record.freight_concept_id.concept_type,
                        'cost_type': record.freight_concept_id.cost_type,
                    })
                                        
    def _compute_real_transit(self):
        for rec in self:
            imports = self.env['ft.import'].search([('route_id', '=', rec.id), ('state', '=', 'port')])
            if imports:
                transit_days = imports.mapped(lambda i: (i.date_arrival_port - i.shipment_date).days)
                rec.real_transit = sum(transit_days)/len(imports)
            else:
                rec.real_transit = 0
                
    @api.depends('freight_rate_ids.freight_price_ref', 'freight_rate_ids.freight_price')
    def _compute_freight_prices(self):
        for rec in self:
            latest_price = rec.freight_rate_ids.filtered(lambda x: (
                x.freight_price
                and x.freight_price_ref
            )).sorted('name')[-1:]
            rec.freight_price = latest_price.freight_price
            rec.freight_price_ref = latest_price.freight_price_ref
    
    @api.onchange('freight_price', 'freight_price_ref', 'freight_concept_id', 'associated_expenses_ids')
    def _onchange_freight_fields(self):
        freight_concept_line = self.associated_expenses_ids.filtered(lambda l: l.product_id.id == self.freight_concept_id.id)
        if freight_concept_line:
            freight_concept_line.fee = self.freight_price
            freight_concept_line.fee_ref = self.freight_price_ref
    
    def unlink(self):
        self.freight_rate_ids.unlink()
        self.associated_expenses_ids.unlink()
        return super(FtImportRoutes, self).unlink()



class ImportRoutesFreightRate(models.Model):
    _name = 'ft.import.routes.freight.rates'
    _description = 'Import Route Freight Rates'
    _order = "name desc"

    route_id = fields.Many2one('ft.import.routes', string="Route")
    name = fields.Datetime(string='Date', required=True, index=True, default=fields.Datetime.now,
                           help="Indicates the date the record was created.")
    currency_id = fields.Many2one('res.currency', string="Currency Ref", default=lambda self: self.env.company.currency_id, ondelete="restrict", readonly=True)
    currency_ref_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_ref_id, ondelete="restrict", readonly=True)
    freight_price = fields.Monetary(string="Freight price", currency_field='currency_id',
                                    help="Indicates the price in ref currency of the freight for the route.")
    freight_price_ref = fields.Monetary(string="Freight price ref", currency_field='currency_ref_id',
                                        help="Indicates the price in ref currency of the freight for the route.")
    start_date = fields.Date('From Date', help="Indicates the initial date of the freight period.")
    end_date = fields.Date('To Date', help="Indicates the end date of the freight period")

    @api.onchange('freight_price')
    def _freight_price_onchange(self):
        if self.freight_price:
            self.freight_price_ref = self.currency_id._convert(self.freight_price, self.currency_ref_id, self.env.company, datetime.now())

    @api.onchange('freight_price_ref')
    def _freight_price_ref_onchange(self):
        if self.freight_price_ref:
            self.freight_price = self.currency_ref_id._convert(self.freight_price_ref, self.currency_id, self.env.company, datetime.now())


