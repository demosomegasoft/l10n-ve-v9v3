# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re
from datetime import date

class DispatchControl(models.Model):
    _name = 'dispatch.control'
    _description = 'Dispatch Control'

    name = fields.Char(string="Name", default=_('New'))
    state = fields.Selection([
            ('pending', 'Pending'),
            ('in_process', 'In process'),
            ('sent', 'Sent'),
            ('customer_withdraws', 'Customer withdraws')], string='State', default='pending')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company)
    sale_order_id = fields.Many2one('sale.order', string="Sale order", readonly=True)
    picking_ids = fields.Many2many('stock.picking', compute="_compute_picking_ids", store=True)
    picking_move_lines = fields.One2many(related='picking_ids.move_ids')
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)
    company_vat = fields.Char(related='invoice_id.company_id.vat')
    partner_id = fields.Many2one(related='sale_order_id.partner_id')
    partner_vat = fields.Char(related='partner_id.vat')
    phone = fields.Char(related='partner_id.phone')
    # Address fields 
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')

    date_issue = fields.Date(string="Date of issue", default=date.today())
    date_delivery = fields.Date(string="Date of delivery", readonly=True)
    user_id = fields.Many2one(related='sale_order_id.user_id')
    driver_id = fields.Many2one('res.partner', string='Transportation', ondelete='restrict', readonly=True)
    description = fields.Text(string="Description")

    product_line_ids = fields.One2many('dispatch.product.line', 'dispatch_control_id', string="Lines")
    calculate_product_line = fields.Boolean(compute='_calculate_product_line', store=True)

    transfers_count = fields.Integer(string='Transfers Count', compute='_get_transfers_count')

    @api.depends('sale_order_id', 'sale_order_id.picking_ids')
    def _compute_picking_ids(self):
        for rec in self:
            rec.picking_ids = rec.sale_order_id.picking_ids.filtered(lambda p: p.picking_type_id.code == 'outgoing')

    def _get_transfers_count(self):
        for rec in self:
            rec.transfers_count = len(self.picking_ids)

    @api.depends('picking_ids', 'picking_ids.move_ids', 'picking_ids.move_ids.quantity_done')
    def _calculate_product_line(self):
        for rec in self:
            rec.calculate_product_line = True
            rec.product_line_ids = [(5,)]
            vals = dict()
            for move in rec.picking_ids.move_ids:
                if vals.get(move.product_id.id, False):
                    vals[move.product_id.id][2]['product_qty'] += move.quantity_done
                else:
                    vals[move.product_id.id] = (0, 0, {
                        'dispatch_control_id': rec.id,
                        'product_id': move.product_id.id,
                        'product_qty': move.quantity_done,
                    })
            rec.product_line_ids = list(vals.values())

    @api.model_create_multi
    def create(self, value_list):
        for values in value_list:
            values['name'] = self.env['ir.sequence'].next_by_code('dispatch.control.sequence') or 'New'
        res = super(DispatchControl, self).create(value_list)
        return res

    def action_view_invoice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = self.invoice_id.id
        return action

    def action_view_transfers(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        action['context'] = {
            'create': 0
        }
        return action

    def customer_withdraws(self):
        self.state = 'customer_withdraws'
        self.date_delivery = date.today()

    # report functions

    def get_number(self, name):
        n = re.findall('([0-9]+$)', name)
        if n:
            return n[0]
        else:
            return name

class DispatchProductLine(models.Model):
    _name = 'dispatch.product.line'
    _description = 'Dispatch Product Line'

    dispatch_control_id = fields.Many2one('dispatch.control', string="Dispatch Control", readonly=True)
    product_id = fields.Many2one('product.product', string="Description", readonly=True)
    code = fields.Char(related='product_id.default_code')
    product_qty = fields.Float(string="Quantity", readonly=True)
    weight = fields.Float(string="Weight", compute="_compute_weight")
    weight_uom_name = fields.Char(related='product_id.product_tmpl_id.weight_uom_name')

    @api.depends('product_id', 'product_qty')
    def _compute_weight(self):
        for line in self:
            line.weight = line.product_id.weight * line.product_qty

