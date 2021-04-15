# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    signature = fields.Binary("Signature")
    num_order = fields.Integer("Nº Order")
    payment_form_str = fields.Text("Payment Form string", compute="_get_payment_form")
    payment_form_str_report = fields.Text(
        "Payment Form string", compute="_get_payment_form"
    )
    contract_text = fields.Text('Contract Text', related="company_id.contract_text")
    legal_text = fields.Text('Legal Text', related="company_id.legal_text")
    recoverable_text = fields.Text('Recoverable Text', related="company_id.recoverable_text")
    recoverable_text2 = fields.Text('Recoverable Text 2', related="company_id.recoverable_text2")

    def _get_payment_form(self):
        for p in self:
            p.payment_form_str = 5 * " " + "EFECTIVO" + 10 * " - " + str(p.amount_total)
            p.payment_form_str_report = "EFECTIVO " + str(p.amount_total)
