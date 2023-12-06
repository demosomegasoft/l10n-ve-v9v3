# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    # Certificare bottom

    certificate_danger_alert = fields.Boolean(
        compute="_compute_certificate_alert")
    certificate_warning_alert = fields.Boolean(
        compute="_compute_certificate_alert")
    certificate_success_alert = fields.Boolean(
        compute="_compute_certificate_alert")
    certificate_muted_alert = fields.Boolean(
        compute="_compute_certificate_alert")

    @api.depends('product_id')
    def _compute_certificate_alert(self):
        for rec in self:
            if rec.requisition_id.vendor_id.person_type_code == 'PJND' or rec.requisition_id.vendor_id.person_type_code == 'PNNR':
                if self.product_certificate_success_alert(rec.product_id):
                    rec.certificate_danger_alert = False
                    rec.certificate_warning_alert = False
                    rec.certificate_success_alert = True
                    rec.certificate_muted_alert = False

                elif self.product_certificate_warning_alert(rec.product_id):
                    rec.certificate_danger_alert = False
                    rec.certificate_warning_alert = True
                    rec.certificate_success_alert = False
                    rec.certificate_muted_alert = False

                elif self.product_certificate_danger_alert(rec.product_id):
                    rec.certificate_danger_alert = True
                    rec.certificate_warning_alert = False
                    rec.certificate_success_alert = False
                    rec.certificate_muted_alert = False

                else:  # muted
                    rec.certificate_danger_alert = False
                    rec.certificate_warning_alert = False
                    rec.certificate_success_alert = False
                    rec.certificate_muted_alert = True

            else:
                rec.certificate_danger_alert = False
                rec.certificate_warning_alert = False
                rec.certificate_success_alert = False
                rec.certificate_muted_alert = False

    def button_pass(self):
        pass

    def product_certificate_success_alert(self, product):
        if any(certificate.state == 'current' for certificate in product.mapped('certificate_ids')):
            return True

    def product_certificate_warning_alert(self, product):
        if any(certificate.state == 'to_expire' for certificate in product.mapped('certificate_ids')):
            return True

    def product_certificate_danger_alert(self, product):
        if any(certificate.state == 'expired' for certificate in product.mapped('certificate_ids')):
            return True
