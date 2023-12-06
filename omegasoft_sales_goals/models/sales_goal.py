# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class SalesGoal(models.Model):
    _name = 'sales.goal'
    _description = 'Sales Goal'
    _rec_name = 'name_date'

    start_date = fields.Date(string="Start Date", required=True, default=lambda self: fields.Date.today().replace(day=1))
    end_date = fields.Date(string="End Date", required=True, compute="_compute_end_date")

    name_date = fields.Char(string="Date")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    line_ids = fields.One2many('sales.goal.line', 'sales_goal_id', string="Goals")

    @api.depends('start_date')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date:
                rec.end_date = rec.start_date + relativedelta(day=31)
            else:
                rec.end_date = False
    
    def name_get(self):
        result = []
        for item in self:
            result.append((item.id,_('%s', item.start_date.strftime("%b/%Y"))))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SalesGoal, self).create(vals_list)
        for rec in res:
            rec.name_date = rec.start_date.strftime("%b/%Y")
        return res

