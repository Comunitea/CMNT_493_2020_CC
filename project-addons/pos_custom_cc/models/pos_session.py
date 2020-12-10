# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _prepare_line(self, order_line):
        """
        OVERWRITED TO GET THE CORRECT REBU AMOUNT TAX
        """
        # import pudb.remote

        # pudb.remote.set_trace(term_size=(271, 64))
        def get_income_account(order_line):
            product = order_line.product_id
            income_account = (
                product.with_context(
                    force_company=order_line.company_id.id
                ).property_account_income_id
                or product.categ_id.with_context(
                    force_company=order_line.company_id.id
                ).property_account_income_categ_id
            )
            if not income_account:
                raise UserError(
                    _(
                        'Please define income account for this \
                       product: "%s" (id:%d).'
                    )
                    % (product.name, product.id)
                )
            return order_line.order_id.fiscal_position_id.map_account(income_account)

        tax_ids = order_line.tax_ids_after_fiscal_position.filtered(
            lambda t: t.company_id.id == order_line.order_id.company_id.id
        )
        sign = -1 if order_line.qty >= 0 else 1
        price = (
            sign * order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        )
        # The 'is_refund' parameter is used to compute the tax tags.
        # Ultimately, the tags are part
        # of the key used for summing taxes. Since the POS UI
        # doesn't support the tags, inconsistencies
        # may arise in 'Round Globally'.

        def check_refund(x):
            return x.qty * x.price_unit < 0

        if self.company_id.tax_calculation_rounding_method == "round_globally":
            is_refund = all(check_refund(line) for line in order_line.order_id.lines)
        else:
            is_refund = check_refund(order_line)

        # REBU
        if order_line.rebu and order_line.lot_id:
            # En venta recuparada, el precio de venta será el coste mas la comisión
            if order_line.lot_id.renew_commission and not order_line.lot_id.salable:
                price = price * (1 + (order_line.lot_id.renew_commission / 100))
            price -= sign * order_line.lot_id.standard_price

        tax_data = tax_ids.compute_all(
            price_unit=price,
            quantity=abs(order_line.qty),
            currency=self.currency_id,
            is_refund=is_refund,
        )
        taxes = tax_data["taxes"]
        # For Cash based taxes, use the account from the repartition line
        # immediately as it has been paid already
        for tax in taxes:
            tax_rep = self.env["account.tax.repartition.line"].browse(
                tax["tax_repartition_line_id"]
            )
            tax["account_id"] = tax_rep.account_id.id
        date_order = order_line.order_id.date_order
        taxes = [{"date_order": date_order, **tax} for tax in taxes]

        # REBU
        fix_amount = order_line.price_subtotal
        if order_line.rebu:
            fix_amount -= order_line.lot_id.standard_price
        return {
            "date_order": order_line.order_id.date_order,
            "income_account_id": get_income_account(order_line).id,
            "amount": fix_amount,  # rebu fix
            "taxes": taxes,
            "base_tags": tuple(tax_data["base_tags"]),
        }

    def _create_non_reconciliable_move_lines(self, data):
        """
        OVEREWRITED TO CREATE BASE EXTRA
        """
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)

        # import pudb.remote

        # pudb.remote.set_trace(term_size=(271, 64))
        taxes = data.get("taxes")
        sales = data.get("sales")
        stock_expense = data.get("stock_expense")
        split_receivables = data.get("split_receivables")
        combine_receivables = data.get("combine_receivables")
        MoveLine = data.get("MoveLine")

        tax_vals = [
            self._get_tax_vals(
                key,
                amounts["amount"],
                amounts["amount_converted"],
                amounts["base_amount_converted"],
            )
            for key, amounts in taxes.items()
            if amounts["amount"]
        ]
        # Check if all taxes lines have account_id assigned. If not,
        # there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [
            line["name"] for line in tax_vals if line["account_id"] is False
        ]
        if len(tax_names_no_account) > 0:
            error_message = _(
                "Unable to close and validate the session.\n"
                "Please set corresponding tax account in each repartition "
                "line of the following taxes: \n%s"
            ) % ", ".join(tax_names_no_account)
            raise UserError(error_message)

        # REBU BASE EXTRA
        amounts = lambda: {"amount": 0.0, "amount_converted": 0.0}
        sales_exent = defaultdict(amounts)
        extra = 0.0
        total_itp_1_3 = 0.0
        example_lot = False
        for pos_line in self.order_ids.mapped("lines"):
            if pos_line.rebu and pos_line.lot_id:
                extra = pos_line.lot_id.standard_price

                line = self._prepare_line(pos_line)
                line["amount"] = extra
                sale_key = (
                    # account
                    line["income_account_id"],
                    # sign
                    -1 if extra < 0 else 1,
                    # for taxes
                    (),
                    (),
                )
                sales_exent[sale_key] = self._update_amounts(
                    sales_exent[sale_key],
                    {"amount": line["amount"]},
                    line["date_order"],
                )
            # ITP 1/3
            if pos_line.lot_id and pos_line.lot_id.itp_1_3:
                example_lot = pos_line.lot_id
                total_itp_1_3 += pos_line.lot_id.itp_1_3

        # REBU BASE EXTRA VALS
        new_extra_base_vals = []
        if extra:
            new_extra_base_vals = [
                self._get_sale_vals(key, amounts["amount"], amounts["amount_converted"])
                for key, amounts in sales_exent.items()
            ]

        itp_1_3_vals = []
        if total_itp_1_3:
            itp_1_3_vals = self.get_itp_1_3_vals(total_itp_1_3, example_lot)

        MoveLine.create(
            tax_vals
            + [
                self._get_sale_vals(key, amounts["amount"], amounts["amount_converted"])
                for key, amounts in sales.items()
            ]
            + new_extra_base_vals  # REBU added
            + itp_1_3_vals  # ITP 1_3 added
            + [
                self._get_stock_expense_vals(
                    key, amounts["amount"], amounts["amount_converted"]
                )
                for key, amounts in stock_expense.items()
            ]
            + [
                self._get_split_receivable_vals(
                    key, amounts["amount"], amounts["amount_converted"]
                )
                for key, amounts in split_receivables.items()
            ]
            + [
                self._get_combine_receivable_vals(
                    key, amounts["amount"], amounts["amount_converted"]
                )
                for key, amounts in combine_receivables.items()
            ]
        )
        return data

    def get_itp_1_3_vals(self, amount, example_lot):
        # related_invoice_line = self.env['account.move.line'].search(
        # [('purchase_line_id', '=', example_lot.purchase_line_id.id)])
        itp_tax = example_lot.purchase_line_id.taxes_id.filtered(lambda x: x.itp)
        # base_rep = itp_tax.invoice_repartition_line_ids.filtered(
        #     lambda x: x.repartition_type == "base"
        # )
        tax_rep = itp_tax.invoice_repartition_line_ids.filtered(
            lambda x: x.repartition_type == "tax"
        )
        if not itp_tax:
            raise UserError(_("No itp tax founded"))

        account_id = (
            example_lot.product_id.categ_id.property_account_expense_categ_id.id
        )
        tax_vals = {
            "debit": amount,
            "credit": 0,
            "name": "BASE ITP 1/3",
            "account_id": account_id,
            "move_id": self.move_id.id,
            "tax_ids": [(6, 0, set())],
            "tag_ids": [(6, 0, ())],
            "tax_repartition_line_id": tax_rep.id,
        }
        purchase_vals = {
            "debit": 0.0,
            "credit": amount,
            "name": "ITP 1/3 " + itp_tax.name,
            "account_id": tax_rep.account_id.id,
            "move_id": self.move_id.id,
            "tax_ids": [(6, 0, set())],
            "tag_ids": [(6, 0, ())],
        }
        return [tax_vals, purchase_vals]
