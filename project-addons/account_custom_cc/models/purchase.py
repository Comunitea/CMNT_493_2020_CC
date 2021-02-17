# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    payment_id = fields.Many2one("account.payment", "Payment", readonly=True)

    def action_instant_payment(self):
        return (
            self.env["account.payment"]
            .with_context(
                active_ids=self.ids, active_model="purchase.order", active_id=self.id
            )
            .action_register_payment()
        )

    def _get_invoice_vals(self, journal):
        res = {
            "ref": self.name,
            "type": "in_invoice",
            "journal_id": journal.id,
            # 'narration': self.note,
            "currency_id": self.currency_id.id,
            "invoice_user_id": self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id,
            "partner_id": self.partner_id,
            # 'partner_shipping_id': self.partner_shipping_id.id,
            # 'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "invoice_origin": self.name,
            "invoice_payment_term_id": self.payment_term_id.id,
            # 'invoice_payment_ref': self.reference,
            # 'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            "invoice_line_ids": [],
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "cc_type": self.cc_type,
        }
        return res

    def create_invoice_payment(self, journal, amount, pos_config):
        self.ensure_one()
        invoice_vals = self._get_invoice_vals(journal)
        for po_line in self.order_line:
            line_vals = po_line._get_invoice_line_vals()
            invoice_vals["invoice_line_ids"].append((0, 0, line_vals))
        invoice = self.env["account.move"].create([invoice_vals])

        invoice.action_post()
        # import pudb.remote
        # pudb.remote.set_trace(term_size=(271, 64))
        # Create bank statement line
        domain = [
            ("state", "=", "open"),
            ("journal_id", "=", journal.id),
            ("pos_session_id.config_id", "=", pos_config.id),
            ("company_id", "=", self.company_id.id),
        ]
        statement = self.env["account.bank.statement"].search(domain)

        if not statement:
            raise UserError(_("Not bank statement open found"))
        # return invoice

        bank_stmt_line = self.env["account.bank.statement.line"].create(
            {
                "name": "payment",
                "statement_id": statement.id,
                "partner_id": self.partner_id.id,
                "amount": -amount,
                "amount_currency": -amount,
                # 'currency_id': self.company_id.currency_id.id,
                "date": fields.Datetime.now(),
            }
        )

        line_id = invoice.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        # amount_in_widget = currency_id and amount_currency or amount
        bank_stmt_line.process_reconciliation(
            counterpart_aml_dicts=[
                {
                    "move_line": line_id,
                    "debit": amount,
                    # 'credit': amount_in_widget > 0 and amount_in_widget or 0.0,
                    "name": line_id.name,
                }
            ]
        )

    # def action_instant_payment_invoice(self, journal, amount):
    #     self.ensure_one()
    #     invoice = self.create_invoice_payment(journal, amount)
    #     return self.action_view_invoice()

    @api.model
    def create(self, vals):
        if vals.get("cc_type") and vals["cc_type"] != "general":
            company_id = vals.get("company_id")
            ref = "account_custom_cc." + str(company_id) + "_" + "fp_exent_purchase"
            fp_exent = self.env.ref(ref)
            if fp_exent:
                vals["fiscal_position_id"] = fp_exent.id
        return super().create(vals)

    def write(self, vals):
        company_id = (
            vals.get("company_id")
            if vals.get("company_id")
            else self.mapped("company_id")[0].id
        )
        if vals.get("cc_type") and vals["cc_type"] != "general":
            ref = "account_custom_cc." + str(company_id) + "_" + "fp_exent_purchase"
            fp_exent = self.env.ref(ref)
            if fp_exent:
                vals["fiscal_position_id"] = fp_exent.id
        return super().write(vals)

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.cc_type != "general":
            company_id = self.company_id.id
            ref = "account_custom_cc." + str(company_id) + "_" + "fp_exent_purchase"
            fp_exent = self.env.ref(ref)
            if fp_exent:
                self.fiscal_position_id = fp_exent.id
        return res


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def prepare_lot_vals(self):
        """
        Propago al lote el coste con ITP, PERO NO EN EL CASO DE RECUPERAR LA
        compra, en ese caso el coste y el precio del producto coincidirán. Lo
        que se cobra a mayores es la comision de renovación.
        """
        res = super().prepare_lot_vals()

        # Add rebu mark
        if self.cc_type != "general":
            res["rebu"] = True

        # Add itp to standard price
        itp_tax = self.taxes_id.filtered(lambda x: x.itp)
        if self.product_id.itp and itp_tax:
            tax_res = itp_tax.compute_all(
                self.price_unit,
                currency=self.currency_id,
                quantity=self.product_qty,
                product=self.product_id,
                partner=self.partner_id,
                is_refund=False,
            )

            # SI ES COMPRA RECUPERABLE EL COSTE SERÁ EL PRECIO DE COMPRA
            # SIN AÑADIR ITP
            if self.cc_type != "recoverable_sale":
                res["standard_price"] = tax_res["total_included"]

            if tax_res["taxes"] and "ITP" in tax_res["taxes"][0]["name"]:
                res["itp_1_3"] = tax_res["taxes"][0]["amount"] - (
                    tax_res["taxes"][0]["amount"] * 2 / 3
                )
        return res

    def _get_invoice_line_vals(self):
        res = {
            "name": "{}: {}".format(self.order_id.name, self.name),
            # 'move_id': move.id,
            # 'currency_id': currency and currency.id or False,
            "purchase_line_id": self.id,
            # 'date_maturity': move.invoice_date_due,
            "product_uom_id": self.product_uom.id,
            "product_id": self.product_id.id,
            "price_unit": self.price_unit,
            "quantity": self.qty_received,
            "partner_id": self.order_id.partner_id.id,
            "analytic_account_id": self.account_analytic_id.id,
            "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
            "tax_ids": [(6, 0, self.taxes_id.ids)],
            "display_type": self.display_type,
            "operating_unit_id": self.operating_unit_id.id,
        }
        return res

    def _compute_tax_id(self):
        """
        OVERWRITED
        Add ITP tax if product manages itp
        """
        for line in self:
            taxes = self.env["account.tax"]
            if line.product_id.itp:
                if (
                    not line.order_id.operating_unit_id
                    or not line.order_id.operating_unit_id.itp_tax_id
                ):
                    raise UserError(
                        _("You need to set the itp tax in the operating unit"),
                    )
                taxes |= line.order_id.operating_unit_id.itp_tax_id
            taxes |= line.product_id.supplier_taxes_id.filtered(
                lambda r: r.company_id == line.order_id.company_id
            )
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.partner_id.with_context(
                    force_company=line.company_id.id
                ).property_account_position_id
            )
            line.taxes_id = (
                fpos.map_tax(taxes, line.product_id, line.order_id.partner_id)
                if fpos
                else taxes
            )

    @api.depends("product_qty", "price_unit", "taxes_id")
    def _compute_amount(self):
        """
        No tax amount in itp product.
        Purchase amount_all will return the excluded price
        """
        res = super()._compute_amount()
        for line in self:
            if line.taxes_id.filtered(lambda x: x.itp):
                line.price_total = line.price_subtotal
                line.price_tax = 0
        return res
