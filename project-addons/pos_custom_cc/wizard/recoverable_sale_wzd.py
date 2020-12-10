from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RecoverableSaleWzd(models.TransientModel):
    _name = "recoverable.sale.wzd"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        line_vals = []
        if self.env.context.get("active_id"):
            purchase = self.env["purchase.order"].browse(
                self.env.context.get("active_id")
            )
            lots = purchase.mapped("order_line.lot_ids")
            # amount = 0
            for lot in lots.filtered(lambda x: x.recovered is False):
                # renew_price = lot.standard_price * (lot.renew_commission / 100)
                renew_price = lot.purchase_line_id.price_unit * (
                    lot.renew_commission / 100
                )
                new_limit_date = datetime.today() + relativedelta(months=1)
                today = datetime.today()
                self.police_date = today
                vals = {
                    "wzd_id": self.id,
                    "lot_id": lot.id,
                    "product_id": lot.product_id.id,
                    "purchase_line_id": lot.purchase_line_id.id,
                    "commission": lot.renew_commission,
                    "price": lot.purchase_line_id.price_unit,  # lot.standard_price itp
                    "renew_price": renew_price,
                    "new_limit_date": new_limit_date,
                }
                line_vals.append((0, 0, vals))
                # amount += lot.list_price
            res.update(line_ids=line_vals)

        product = self.env.ref("product_serial_number.product_renovate_commission")
        if product:
            res.update(product_id=product.id)
        return res

    mode = fields.Selection(
        [("sale", "Sale"), ("renew", "Renew")], "Mode", required=True, default="sale"
    )
    product_id = fields.Many2one("product.product", "Product", required=True)
    payment_method_id = fields.Many2one(
        "pos.payment.method", "Payment Method", required=True
    )
    amount = fields.Float("Amount", required=True)
    line_ids = fields.One2many("recoverable.sale.line.wzd", "wzd_id", "Manage products")

    @api.onchange("line_ids", "mode")
    def onchange_mode_or_lines(self):
        if self.mode == "sale":
            amount = sum([x.price for x in self.line_ids])
            amount += sum([(x.price * x.commission / 100) for x in self.line_ids])
            self.amount = amount
        else:
            self.amount = sum([x.renew_price for x in self.line_ids])

    def get_statement_lines(self):
        vals = {
            "name": fields.Datetime.to_string(fields.datetime.now()),
            "payment_method_id": self.payment_method_id.id,
            "amount": self.amount,
            "payment_status": "",
            "ticket": "",
            "card_type": "",
            "transaction_id": "",
        }
        res = [[0, 0, vals]]
        return res

    def button_sale(self, renovate=False):
        # import pudb.remote
        # pudb.remote.set_trace(term_size=(271, 64))
        if self.env.context.get("active_id"):
            purchase = self.env["purchase.order"].browse(
                self.env.context.get("active_id")
            )
            line_vals_lst = []
            amount_total = 0
            amount_tax = 0
            for line in self.line_ids:
                # GET POS ORDER LINES
                line_vals = line.get_line_vals(purchase, renovate)
                line_vals_lst.append((0, 0, line_vals))
                # Get totals
                amount_total += line_vals["price_subtotal_incl"]
                amount_tax += (
                    line_vals["price_subtotal_incl"] - line_vals["price_subtotal"]
                )
                if self.mode == "sale":
                    # GET wxtra line commission
                    line_vals = line.get_line_vals(purchase, True)
                    line_vals_lst.append((0, 0, line_vals))
                    # Get totals
                    amount_total += line_vals["price_subtotal_incl"]
                    amount_tax += (
                        line_vals["price_subtotal_incl"] - line_vals["price_subtotal"]
                    )

            # GET STATEMENT LINES
            statement_lst = self.get_statement_lines()

            domain = [("state", "=", "opened")]
            pos_session = self.env["pos.session"].search(domain, limit=1)
            if not pos_session:
                raise UserError(
                    _("No pos session founded"),
                    _("You need to open a pos session"),
                )

            creation_date = fields.Datetime.to_string(fields.datetime.now())
            name_mode = _("Recoverable sale ")
            if renovate:
                name_mode = _("Renew ")
            name = name_mode + str(purchase.name) + " " + creation_date
            order_vals = {
                "name": name,
                "amount_paid": self.amount,
                "amount_total": amount_total,
                "amount_tax": amount_tax,
                "amount_return": self.amount - amount_total,
                "lines": line_vals_lst,
                "statement_ids": statement_lst,
                "pos_session_id": pos_session.id,
                "pricelist_id": 1,
                "partner_id": purchase.partner_id.id,
                "user_id": self._uid,
                "employee_id": False,
                "uid": name,
                "sequence_number": 1,
                "creation_date": creation_date,
                "fiscal_position_id": False,
                "server_id": False,
                "to_invoice": False if not renovate else True,
            }
            data_dic_lst = [
                {
                    "id": name,
                    "data": order_vals,
                    "to_invoice": False if not renovate else True,
                }
            ]

            orders_sr = self.env["pos.order"].create_from_ui(data_dic_lst)
            if orders_sr:
                pos_order = self.env["pos.order"].browse(orders_sr[0]["id"])
                pos_order.purchase_id = purchase.id

            self.update_lot_renew_finish(renovate, purchase)
        return

    def button_renovate(self):
        self.button_sale(renovate=True)
        return

    def update_lot_renew_finish(self, renovate, purchase):
        if renovate:
            for line in self.line_ids:
                lot = line.lot_id
                lot.write(
                    {"num_renew": lot.num_renew + 1, "limit_date": line.new_limit_date}
                )
        else:
            self.line_ids.mapped("lot_id").write({"recovered": True, "itp_1_3": 0})

            # Check if finished recoverable sale
            if all([x.recovered for x in purchase.mapped("order_line.lot_ids")]):
                purchase.all_recovered = True
        return


class RecoverableSaleLineWzd(models.TransientModel):
    _name = "recoverable.sale.line.wzd"

    wzd_id = fields.Many2one("recoverable.sale.wzd", "Wzd")
    lot_id = fields.Many2one("stock.production.lot", "Lot", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    purchase_line_id = fields.Many2one(
        "purchase.order.line", "Purchase line", readonly=True
    )
    commission = fields.Float("Commission")
    price = fields.Float("PVP")
    limit_date = fields.Date("Limit date", related="lot_id.limit_date")
    new_limit_date = fields.Date("New limit date")
    renew_price = fields.Float("Renew amount")

    @api.onchange("commission")
    def onchange_commission(self):
        # self.renew_price = self.lot_id.standard_price * (self.commission / 100)
        self.renew_price = self.lot_id.purchase_line_id.price_unit * (
            self.commission / 100
        )

    def get_tax_ids(self, purchase, renovate):
        """
        Return rebu map taxes or RC product taxes
        """
        self.ensure_one()

        product = self.product_id
        if renovate:
            product = self.env.ref("product_serial_number.product_renovate_commission")

        company = purchase.company_id
        taxes = product.taxes_id.filtered(lambda r: r.company_id == company)

        if renovate:
            return [[6, 0, [x.id for x in taxes]]]

        ref = "account_custom_cc." + str(company.id) + "_" + "fp_rebu"
        fp_rebu = self.env.ref(ref)
        rebu_taxes = fp_rebu.map_tax(taxes, self.product_id, False)
        tax_ids = []
        if rebu_taxes:
            tax_ids = [r.id for r in rebu_taxes]
        res = [[6, 0, tax_ids]]
        return res

    def get_pack_lot_ids(self):
        self.ensure_one()
        dic = {"lot_name": self.lot_id.name}
        res = [[0, 0, dic]]
        return res

    def get_line_vals(self, purchase, renovate):
        self.ensure_one()
        taxes_vals = self.get_tax_ids(purchase, renovate)

        taxes = self.env["account.tax"]
        for tv in taxes_vals:
            tax_ids = tv[2]
            taxes |= self.env["account.tax"].browse(tax_ids)

        price = self.price if not renovate else self.renew_price

        price_compute = price
        # REBU
        if self.lot_id.rebu and not renovate:
            price_compute = (
                price * (1 + (self.commission / 100))
            ) - self.lot_id.standard_price
        tax_res = taxes.compute_all(
            price_compute,
            currency=purchase.company_id.currency_id,
            quantity=1,
            product=self.product_id,
            partner=purchase.partner_id,
            is_refund=False,
        )
        tax_amount = tax_res["total_included"] - tax_res["total_excluded"]
        product = self.product_id
        if renovate:
            product = self.env.ref("product_serial_number.product_renovate_commission")
        res = {
            "qty": 1,
            "price_unit": price,
            "price_subtotal_incl": price,
            "price_subtotal": price - tax_amount,
            "discount": 0,
            "product_id": product.id,
            "tax_ids": taxes_vals,
            "id": purchase.id,  # Se necesita un id diferente en cada sesión
            "pack_lot_ids": self.get_pack_lot_ids() if not renovate else [],
            "lot_id": self.lot_id.id if not renovate else [],
            "cost": self.lot_id.standard_price if not renovate else 0,
            "rebu": self.lot_id.rebu if not renovate else False,
            "description": self.product_id.name + " - " + self.lot_id.name
            if renovate
            else "",
        }
        return res
