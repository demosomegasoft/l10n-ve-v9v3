# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FtImport(models.Model):
    _name = 'ft.import'
    _description = 'Foreign Trade Imports'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Reference", default=_('New folio'))
    purchase_ids = fields.One2many('purchase.order', 'import_id', string="Purchase order", tracking=True,
                                   required=True, help="Establishes the purchase orders that will be managed in the import process.")
    delivery_note_ids = fields.Many2many('stock.picking', string="Delivery note", compute='_compute_purchase_transfers', tracking=True, readonly=True,
                                    help="Indicates the number of delivery notes that are associated with purchases in the import process.")
    customs_agent_id = fields.Many2one('res.partner', string="Customs agent", domain=[('customs_agent', '=', True)], tracking=True, ondelete='cascade',
                                    help="Indicates the name of the customs agent who will manage the import")
    route_id = fields.Many2one('ft.import.routes', string="Import route", tracking=True, ondelete="restrict",
                                    help="Indicates the maritime route by which the merchandise will be transported.")
    shipping_company_id = fields.Many2one('ft.shipping.companies', string="Shipping company", readonly=True, ondelete="restrict", tracking=True,
                                    help='Indicates the shipping company that will manage the merchandise')
    origin_port_id = fields.Many2one('ft.ports', string="Origin Port", readonly=True, ondelete="restrict", tracking=True,
                                    help='Port where the merchandise will be dispatched')
    intermediate_1 = fields.Many2one('ft.ports', string="Intermediate 1", readonly=True, ondelete="restrict", tracking=True,
                                    help='Port en route where the shipping company will stop before reaching the destination.')
    intermediate_2 = fields.Many2one('ft.ports', string="Intermediate 2", readonly=True, ondelete="restrict", tracking=True,
                                    help='Port en route where the shipping company will stop before reaching the destination.')
    intermediate_3 = fields.Many2one('ft.ports', string="Intermediate 3", readonly=True, ondelete="restrict", tracking=True,
                                    help='Port en route where the shipping company will stop before reaching the destination.')
    destination_id = fields.Many2one('ft.ports', string="Destination port", readonly=True, ondelete="restrict", tracking=True,
                                    help='Port where the merchandise will be received')
    free_days = fields.Integer(string="Free day", readonly=True, tracking=True,
                                    help='Indicates the days off established by the shipping company on the established route')
    real_transit = fields.Float(string="Real Transit", readonly=True, tracking=True,
                                    help='Indicates the estimated average real time of the merchandise based on the aforementioned imports.')
    storage_id = fields.Many2one('ft.storage', string="Warehouse", ondelete='restrict', tracking=True,
                                    help="Indicates the warehouse that will manage the products in the import process.")
    number_container = fields.Integer(string="Container number", compute="_compute_nro_containers", store=True,
                                    help="Number of containers registered in the import process")
    shipment_date = fields.Date(string="shipment date", tracking=True,
                                    help="Date of shipment of the merchandise from the port of origin")
    dispatch_date = fields.Date(string="Dispatch Date", tracking=True,
                                    help="Dispatch date of the merchandise when it is downloaded from the shipping company")
    date_arrival_port = fields.Date(string="Date Arrival at port", tracking=True,
                                    help="Date of arrival at the port of the merchandise")
    empty_return_date = fields.Date(string="Empty return date", tracking=True,
                                    help="Empty container return date.")
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterm", ondelete="restrict", tracking=True,
                                    help="International trade terms are a series of commercial conditions used in international transactions.")
    label_ids = fields.Many2many('ft.label', string="Label", ondelete="restrict", tracking=True,
                                    help="It is used to establish a category for the import")
    state = fields.Selection([
		('new', 'New'),
		('prod', 'In Production'),
		('ship', 'Coordinating Shipment'),
		('nav', 'Navigating'),
		('port', 'In Port'),
		('received', 'Received'),
		('closed_folio', 'Closed folio'),
		('cancel', 'Canceled')
	], string='Stage', tracking=True, default='new', readonly=True)
    
    incoming_picking_count = fields.Integer("Incoming Shipment count", compute='_compute_incoming_picking_count')
    purchase_order_count = fields.Integer(compute="_compute_origin_po_count", string='Purchase Order Count')

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                    help='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True,
                                    help="Set active to false to hide the children tag without removing it.")
    
    #Binnacle
    binnacle_ids = fields.One2many('ft.binnacle', 'import_id', string="Binnacle",
                                   readonly=False, states={'closed_folio': [('readonly', True)]})
    
    #Container
    container_ids = fields.One2many('ft.import.container', 'import_id',
                                    readonly=False, states={'closed_folio': [('readonly', True)]})
    #Customs Agent (page)
    file_number = fields.Char(string="File number", tracking=True, help="Indicates the number of the import file")
    file_date = fields.Date(string="File date", tracking=True, help="Establishes the date of issuance of the import file.")
    import_form = fields.Char(string="Import Form", tracking=True, help="Indicates the import form No.")
    form_nr_86 = fields.Char(string="Form No.86", tracking=True, help="Indicates Form No. 86")
    form_dav = fields.Char(string="DAV Form", tracking=True, help="Indicates the DAV Form Number")
    bill_landing = fields.Char(string="Bill of landing", tracking=True, help="indicates the Bill of Landing Number in the import process")
    
    #forecast
    forecast_id = fields.One2many('ft.forecast', 'import_id', string="Forecast")
    forecast_purchase_order = fields.Integer(compute="_compute_origin_po_count")
    
    #account
    account_move_ids = fields.One2many('account.move', 'import_id', string="Account move")
    account_move_count = fields.Integer(compute="_compute_account_move_count")
    
    #payments
    payment_count = fields.Integer(compute="_compute_account_move_count")    
    
    #Page Document
    name_document_1 = fields.Char()
    document_1 = fields.Binary(string="Document")
    name_document_2 = fields.Char()
    document_2 = fields.Binary(string="Document")
    name_document_3 = fields.Char()
    document_3 = fields.Binary(string="Document")
    name_document_4 = fields.Char()
    document_4 = fields.Binary(string="Document")
    name_document_5 = fields.Char()
    document_5 = fields.Binary(string="Document")
    name_document_6 = fields.Char()
    document_6 = fields.Binary(string="Document")
    name_document_7 = fields.Char()
    document_7 = fields.Binary(string="Document")
    name_document_8 = fields.Char()
    document_8 = fields.Binary(string="Document")
    name_document_9 = fields.Char()
    document_9 = fields.Binary(string="Document")
    name_document_10 = fields.Char()
    document_10 = fields.Binary(string="Document")
    
    description_1 = fields.Char(string="Description")
    description_2 = fields.Char(string="Description")
    description_3 = fields.Char(string="Description")
    description_4 = fields.Char(string="Description")
    description_5 = fields.Char(string="Description")
    description_6 = fields.Char(string="Description")
    description_7 = fields.Char(string="Description")
    description_8 = fields.Char(string="Description")
    description_9 = fields.Char(string="Description")
    description_10 = fields.Char(string="Description")
    
    @api.onchange('route_id')
    def _onchange_fields_route_id(self):
        for rec in self:
            if rec.state in ['new', 'prod', 'ship']:
                rec.shipping_company_id = rec.route_id.shipping_company_id
            rec.origin_port_id = rec.route_id.origin_routes
            rec.intermediate_1 = rec.route_id.intermediate_1
            rec.intermediate_2 = rec.route_id.intermediate_2
            rec.intermediate_3 = rec.route_id.intermediate_3
            rec.destination_id = rec.route_id.destination_id
            rec.free_days = rec.route_id.free_days
            rec.real_transit = rec.route_id.real_transit
    
    def action_view_picking(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', 'in', self.delivery_note_ids.ids)]
        action['context'] = {
			'create': False,
		}
        return action
    
    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        action['domain'] = [('id', 'in', self.purchase_ids.ids)]
        action['context'] = {
			'create': False,
		}
        return action
    
    def action_view_account_move(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action['domain'] = [('id', 'in', self.account_move_ids.ids)]
        action['context'] = {
			'create': False,
            'default_move_type': 'in_invoice',
		}
        return action
    
    def action_view_payments(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments_payable")
        action['domain'] = [('id', 'in', self.account_move_ids.line_ids.matched_debit_ids.debit_move_id.move_id.payment_ids.ids)]
        action['context'] = {
			'create': False,
		}
        return action
    
    def action_view_forecast(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("omegasoft_foreing_trade_import.ft_forecast_action")
        action['domain'] = [('id', '=', self.forecast_id.id)]
        action['view_mode'] = 'form'
        action['context'] = {'create': False}
        return action
    
    @api.depends('delivery_note_ids')
    def _compute_incoming_picking_count(self):
        for order in self:
            order.incoming_picking_count = len(order.delivery_note_ids)
            
    @api.depends('purchase_ids')
    def _compute_origin_po_count(self):
        for record in self:
            record.purchase_order_count = len(record.purchase_ids)
            record.forecast_purchase_order = 1 if record.purchase_ids else 0
    
    @api.depends('account_move_ids')
    def _compute_account_move_count(self):
        for record in self:
            record.account_move_count = len(record.account_move_ids)
            record.payment_count = len(record.account_move_ids.line_ids.matched_debit_ids.debit_move_id.move_id.payment_ids)

    @api.depends('purchase_ids.picking_ids', 'purchase_ids')
    def _compute_purchase_transfers(self):
        for rec in self:
            rec.delivery_note_ids = [(4, picking.id) for picking in rec.purchase_ids.picking_ids]
    
    @api.depends('container_ids')
    def _compute_nro_containers(self):
        for rec in self:
            rec.number_container = len(rec.container_ids)
            
    @api.model_create_multi
    def create(self, value_list):
        for values in value_list:
            values['name'] = self.env['ir.sequence'].next_by_code('ft.import.sequence') or 'New folio'
            if not 'forecast_id' in values:
                forecast_id = self.env['ft.forecast'].sudo().create([{
                    'nationalization_rate': 1
                }])
                values['forecast_id'] = forecast_id
        res = super().create(value_list)
        return res
    
    def unlink(self):
        for record in self:
            if record.state != 'new' or (record.purchase_ids.filtered(lambda purchase_order: purchase_order.state == 'purchase') or record.delivery_note_ids.filtered(lambda p: p.state == 'done')):
                raise UserError(_("They can only be deleted if they are in the stage again, and also do not have any confirmed Purchase Order or delivery note"))
        self.binnacle_ids.unlink()
        self.container_ids.unlink()
        return super(FtImport, self).unlink()
    
    def button_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('omegasoft_foreing_trade_import.mail_template_document_import')
        attachment_vals=[]
        if self.document_1:
            attachment_vals.append({
                'datas': self.document_1,
                'name': self.name_document_1 if self.name_document_1 else self.name,
            })
        if self.document_2:
            attachment_vals.append({
                'datas': self.document_2,
                'name': self.name_document_2 if self.name_document_2 else self.name,
            })
        if self.document_3:
            attachment_vals.append({
                'datas': self.document_3,
                'name': self.name_document_3 if self.name_document_3 else self.name,
            })
        if self.document_4:
            attachment_vals.append({
                'datas': self.document_4,
                'name': self.name_document_4 if self.name_document_4 else self.name,
            })
        if self.document_5:
            attachment_vals.append({
                'datas': self.document_5,
                'name': self.name_document_5 if self.name_document_5 else self.name,
            })
        if self.document_6:
            attachment_vals.append({
                'datas': self.document_6,
                'name': self.name_document_6 if self.name_document_6 else self.name,
            })
        if self.document_7:
            attachment_vals.append({
                'datas': self.document_7,
                'name': self.name_document_7 if self.name_document_7 else self.name,
            })
        if self.document_8:
            attachment_vals.append({
                'datas': self.document_8,
                'name': self.name_document_8 if self.name_document_8 else self.name,
            })
        if self.document_9:
            attachment_vals.append({
                'datas': self.document_9,
                'name': self.name_document_9 if self.name_document_9 else self.name,
            })
        if self.document_10:
            attachment_vals.append({
                'datas': self.document_10,
                'name': self.name_document_10 if self.name_document_10 else self.name,
            })
        attachment = self.env['ir.attachment'].create(attachment_vals)
        
        if attachment:
            template_id.write({'attachment_ids': [(6, 0, attachment.ids)]})
        return {
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'target': 'new',
			'context': {
				'default_model': 'ft.import',
				'default_res_id': self.id,
				'default_use_template': bool(template_id.id),
				'default_template_id': template_id.id,
				'default_composition_mode': 'comment',
				'default_email_layout_xmlid': 'mail.mail_notification_light',
			},
		}
			
    def action_new(self):
        self.write({
            'state': 'new'
        })

    def action_prod(self):
        self.write({
            'state': 'prod'
        })

    def action_ship(self):
        self.write({
            'state': 'ship',
        })

    def action_nav(self):
        self.write({
            'state': 'nav'
        })

    def action_port(self):
        self.write({
            'state': 'port'
        })

    def action_received(self):
        self.write({
            'state': 'received'
        })

    def action_closed_folio(self):
        self.write({
            'state': 'closed_folio'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    
