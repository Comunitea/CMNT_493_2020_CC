# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    signature = fields.Binary('Signature')
    payment_form_str = fields.Text(
        'Payment Form string', compute="_get_payment_form")
    payment_form_str_report = fields.Text(
        'Payment Form string', compute="_get_payment_form")
    
    def _get_payment_form(self):
        for p in self:
            p.payment_form_str = 5*" " + "EFECTIVO" + 10*" - " + str(p.amount_total)
            p.payment_form_str_report = "EFECTIVO " + str(p.amount_total)
