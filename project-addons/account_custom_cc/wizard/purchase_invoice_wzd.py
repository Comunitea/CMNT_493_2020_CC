from odoo import api, fields, models


class PurchaseInvoiceWzd(models.TransientModel):
    _name = "purchase.invoice.wzd"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_id"):
            purchase = self.env["purchase.order"].browse(
                self.env.context.get("active_id")
            )
            res.update(amount=purchase.amount_total)

        # Create bank statement line
        # domain = [
        #     ("state", "=", "open"),
        #     ("company_id", "=", purchase.company_id.id),
        # ]
        # statement = self.env["account.bank.statement"].search(domain, limit=1)
        # if statement:
        #     res.update(journal_id=statement.journal_id.id)
        return res

    journal_id = fields.Many2one("account.journal", "Journal", required=True)
    amount = fields.Float("Amount", required=True)
    pos_config_id = fields.Many2one("pos.config", string="TpV", required=True)

    @api.onchange('pos_config_id')
    def _onchange_pos_config_id(self):
        res = {}
        if self.pos_config_id and self.pos_config_id.payment_method_ids:
            domain = [('id', 'in',  self.pos_config_id.payment_method_ids.mapped('cash_journal_id').ids)]
            res = {'domain': {'journal_id': domain}}
        return res

    def confirm(self):
        purchase_ids = self._context.get("active_ids")
        purchases = self.env["purchase.order"].browse(purchase_ids)
        for po in purchases:
            po.create_invoice_payment(self.journal_id, self.amount, self.pos_config_id)
        return
