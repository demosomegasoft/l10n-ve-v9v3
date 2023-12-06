# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FtContainers(models.Model):
    _name = 'ft.containers'
    _description = 'Ft Containers'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    name = fields.Char(string="Name", required=True, tracking=True, help="Indicates the name of the container type")
    code = fields.Char(string="Reference", tracking=True, help="Indicates the reference with which the container can be known")
    active_container = fields.Boolean(string="active container", tracking=True, default=True, help="Enabling or disabling this option will hide the container view in other models, eg Purchases, Inventory, Imports.\
                                    This option allows you to hide the container without the need to delete or archive the registry to reduce information that is not normally used.")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', help='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the children tag without removing it.")
    delete_container = fields.Boolean(default=False, groups="omegasoft_foreing_trade_import.group_admin_imports")

    # Dimensions
    inside_length = fields.Float('Inside Length', tracking=True, help="Indicates the dimensions in meters of the container")
    inside_length_uom_id = fields.Many2one('uom.uom', string='Inside Length UOM', default=lambda s: s.env.ref('uom.product_uom_meter'))
    
    inside_width = fields.Float('Inside Width', tracking=True, help="Indicates the dimensions in meters of the container")
    inside_width_uom_id = fields.Many2one('uom.uom', string='Inside Width UOM', default=lambda s: s.env.ref('uom.product_uom_meter'))
    
    inside_height = fields.Float('Inside Height', tracking=True, help="Indicates the dimensions in meters of the container")
    inside_height_uom_id = fields.Many2one('uom.uom', string='Inside Height UOM', default=lambda s: s.env.ref('uom.product_uom_meter'))
    
    door_width = fields.Float('Door Width', tracking=True, help="Indicates the dimensions in meters of the container")
    door_width_uom_id = fields.Many2one('uom.uom', string='Door Width UOM', default=lambda s: s.env.ref('uom.product_uom_meter'))
    
    door_height = fields.Float('Door Height', tracking=True, help="Indicates the dimensions in meters of the container")
    door_height_uom_id = fields.Many2one('uom.uom', string='Door Height UOM', default=lambda s: s.env.ref('uom.product_uom_meter'))

    # Capacity
    cubic_capacity = fields.Float('Cubic Capacity', tracking=True, help="Indicates the maximum volume that the container can carry")
    cubic_capacity_uom_id = fields.Many2one('uom.uom', string='Cubic Capacity UOM', default=lambda s: s.env.ref('uom.product_uom_cubic_foot'))

    tare = fields.Float('Tare', tracking=True, help="Indicates the weight of the container without merchandise in kg.")
    tare_uom_id = fields.Many2one('uom.uom', string='Tare UOM', default=lambda s: s.env.ref('uom.product_uom_kgm'))

    maximum_load = fields.Float('Maximum Load', tracking=True, help="Indicates the maximum weight that the container can contain in Kg.")
    maximum_load_uom_id = fields.Many2one('uom.uom', string='Maximum Load UOM', default=lambda s: s.env.ref('uom.product_uom_kgm'))

    _sql_constraints = [
        ('code_uniq', 'unique (code, company_id)', 'The code must be unique per company!')
    ]
    
    def unlink(self):
        for record in self:
            if record.delete_container:
                raise ValidationError(_("the reference: %s cannot be removed from the model, it can only be archived", record.code))
        return super(FtContainers, self).unlink()