# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError

class GoodsMovementAuthorization(models.Model):
    _name = 'movement.authorization'
    _description = 'Goods Movement Authorization'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _rec_name = 'date'

    name = fields.Char('Name', default=_('New'))
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Validated'),
    ], string='state', default='in_progress', tracking=True)
    date = fields.Date('Date', required=True, default=date.today(), tracking=True)
    sealing = fields.Char('Sealing', default= lambda self: self.env['ir.sequence'].next_by_code('goods.movement.sealing.sequence'))

    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")

    # driver and  vehicle fields
    driver_domain_ids = fields.Many2many('res.partner', string='Driver Domain', compute="_compute_driver_domain")
    driver_id = fields.Many2one('res.partner', string='Driver', required=True, ondelete='restrict', tracking=True)
    vat = fields.Char('Identification', related="driver_id.vat")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='restrict', tracking=True)
    brand_id = fields.Many2one(string='Brand', related="vehicle_id.model_id.brand_id")
    color = fields.Char('Color', related="vehicle_id.color")
    license_plate = fields.Char('License Plate', related="vehicle_id.license_plate")

    dispatch_control_ids = fields.Many2many('dispatch.control', string='Gestión de despacho', ondelete='restrict')
    
    shipping_tables = fields.Html(readonly=True)

    @api.model_create_multi
    def create(self, value_list):
        for values in value_list:
            values['name'] = self.env['ir.sequence'].next_by_code('goods.movement.authorization.sequence') or _('New')
        res = super(GoodsMovementAuthorization, self).create(value_list)
        return res

    @api.depends('date')
    def _compute_driver_domain(self):
        for rec in self:
            query = """
                SELECT 
                    partner.id
                FROM
                    res_partner partner
                    JOIN fleet_vehicle vehicle ON vehicle.driver_id = partner.id
                WHERE
                    vehicle.company_id = {company}
            """.format(company=rec.company_id.id)
            rec._cr.execute(query)
            rec.driver_domain_ids = [(6,0, [res[0] for res in rec._cr.fetchall()])]

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        if self.driver_id:
            query = """
                SELECT 
                    id
                FROM
                    fleet_vehicle vehicle
                WHERE
                    vehicle.driver_id = {partner}
                    AND company_id = {company}
            """.format(partner=self.driver_id.id, company=self.company_id.id)
            self._cr.execute(query)
            result = self._cr.fetchall()
            if result and len(result) == 1:
                self.vehicle_id = result[0][0]
            else:
                self.vehicle_id = False
        else:
            self.vehicle_id = False

    @api.onchange('dispatch_control_ids')
    def _onchange_dispatch_control_ids(self):
        resul = list(set(self._origin.dispatch_control_ids.ids) - set(self.dispatch_control_ids.ids))
        if len(resul) > 0:
            if len(resul) == 1:
                query = """
                    UPDATE dispatch_control
                    SET state = 'pending'
                    WHERE id = {id};
                """.format(id=resul[0])
            else:
                query = """
                    UPDATE dispatch_control
                    SET state = 'pending'
                    WHERE id in {id};
                """.format(id=tuple(resul))
            self._cr.execute(query)
        tables = """"""
        for line in self.dispatch_control_ids:
            line.state = 'in_process'
            tables += _("""
            <br/>
            <table>
                <tr>
                    <th style="border-right: 1px solid black;">Compañía</th>
                    <td>{company}</td>
                </tr>
                <tr>
                    <th style="border-right: 1px solid black">RIF</th>
                    <td>{vat}</td>
                </tr>
                <tr>
                    <th style="border-right: 1px solid black">Dirección</th>
                    <td>{address}</td>
                </tr>
            </table> 
            <br>
            """).format(
                company=line.partner_id.name,
                vat=line.partner_id.vat,
                address= ((line.street2 + ', ') if line.street2 else '') + ((line.street + ', ') if line.street else '') + ((line.city + ', ') if line.city else '') + ((line.state_id.name + ', ') if line.state_id else '') + ((_('zip code ') + line.zip)  if line.zip else '')
                )
        
        self.shipping_tables = tables

    def validate(self):
        self.state = 'done'
        self.dispatch_control_ids.date_delivery = date.today()
        self.dispatch_control_ids.state = 'sent'
        self.dispatch_control_ids.driver_id = self.driver_id

    def get_date_string(self):
        return self.date.strftime(_("%d of %B of %Y"))

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_("Validated authorizations cannot be deleted."))
            rec.dispatch_control_ids.write({
                'state': 'pending'
            })
        return super().unlink()