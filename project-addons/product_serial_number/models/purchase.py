# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def _compute_count_lots(self):
        for order in self:
            order.count_lots = len(order.mapped("order_line.lot_ids"))

    # @api.depends('order_line.renew_commission', 'order_line.price_subtotal')
    def _compute_recoverable_tax(self):
        for order in self:
            recoverable_sale_total_untaxed = 0
            recoverable_sale_total = 0
            recoverable_tax = 0
            if order.cc_type == 'recoverable_sale':
                for line in order.order_line:
                    # TODO no siempre 21%
                    com_amount = line.renew_price - line.price_unit
                    recoverable_sale_total += line.renew_price
                    com_tax = com_amount - (com_amount / 1.21)
                    recoverable_tax += com_tax
                    recoverable_sale_total_untaxed += line.renew_price - com_tax

            order.recoverable_sale_total = recoverable_sale_total
            order.recoverable_sale_total_untaxed = recoverable_sale_total_untaxed
            order.recoverable_tax = recoverable_tax
            order.recoverable_tax_total = recoverable_sale_total_untaxed + recoverable_tax

    count_lots = fields.Integer("Lots", compute="_compute_count_lots")

    recoverable_sale_total = fields.Float(
        'Recoverable Sale Total', compute='_compute_recoverable_tax')
    recoverable_sale_total_untaxed = fields.Float(
        'Recoverable Sale Total Untaxed', compute='_compute_recoverable_tax')
    recoverable_tax = fields.Float(
        'Recoverable Tax', compute='_compute_recoverable_tax')
    recoverable_tax_total = fields.Float(
        'Recoverable Tax Total', compute='_compute_recoverable_tax')

    cc_type = fields.Selection(
        [
            ("normal", "Special"),  # REBU
            ("general", "General"),  # Normal IVA
            ("deposit", "Deposit"),
            ("recoverable_sale", "Recoverable"),
        ],
        "Purchase usage",
        default="normal",
    )
    all_recovered = fields.Boolean(
        "All products recovered", readonly=True, copy=False, default=False
    )

    def _create_picking(self):
        """
        Automatic create serial numbers using dependency oca module.
        Copy purchase lot info to the serial numbers created.
        """
        res = super()._create_picking()
        for po in self:
            pickings = po.picking_ids.filtered(lambda x: x.state == "assigned")
            for pick in pickings:
                # Si no escribo la cantidad hecha no se queda en done el
                # albarán en el button validate
                for move in pick.move_line_ids:
                    move.qty_done = 1
                pick.button_validate()

            # Copy serial number info to the line
            for line in po.order_line:
                lot_ids = line.mapped("move_ids.move_line_ids.lot_id")
                if not lot_ids:
                    continue
                vals = line.prepare_lot_vals()
                if vals:
                    lot_ids.write(vals)
        return res

    def view_lots_button(self):
        self.ensure_one()
        lots = self.mapped("order_line.lot_ids")
        action = self.env.ref("stock.action_production_lot_form").read()[0]
        if len(lots) > 1:
            action["domain"] = [("id", "in", lots.ids)]
        elif len(lots) == 1:
            form_view_name = "stock.view_production_lot_form"
            action["views"] = [(self.env.ref(form_view_name).id, "form")]
            action["res_id"] = lots.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    # def _get_destination_location(self):
    #     self.ensure_one()
    #     res = super()._get_destination_location()
    #     if self.cc_type in ("recoverable_sale", "deposit"):
    #         loc = self.env["stock.location"].search(
    #             [("cc_type", "=", self.cc_type)], limit=1
    #         )
    #         if loc:
    #             return loc.id

    #     return res

    def button_confirm(self):
        if not self._context.get("skyp_dys"):
            for line in self.mapped("order_line"):
                if line.police and not line.police_date:
                    raise UserError(
                        _(
                            "Product {} requires "
                            "police date".format(line.product_id.name)
                        )
                    )
                if (
                    line.cc_type in ("recoverable_sale", "deposit")
                    and not line.limit_date
                ):
                    raise UserError(
                        _(
                            "Product {} requires "
                            "limit date".format(line.product_id.name)
                        )
                    )
                if line.cc_type in ("recoverable_sale") and not line.renew_commission:
                    raise UserError(
                        _(
                            "Product {} requires "
                            "renew commission".format(line.product_id.name)
                        )
                    )
                line.check_constraints()
        res = super().button_confirm()
        return res

    @api.onchange("order_line")
    def onchange_dysfuncionality_ids(self):
        res = {}
        for line in self.order_line:
            mandatory_acess = line.product_id.accessory_ids.filtered("mandatory")
            if mandatory_acess:
                diff_access = mandatory_acess - line.accessory_ids.filtered("mandatory")
                if diff_access:
                    acc_names = ",".join(diff_access.mapped("name"))
                    msg = _("Product %s should have " "this accesories: %s") % (
                        line.product_id.name,
                        acc_names,
                    )
                    warning = {"title": _("Requires Accesories"), "message": msg}
                    res["warning"] = warning
                    return res


class PurchaseOrderLine(models.Model):

    _name = "purchase.order.line"
    _inherit = [_name, "base_multi_image.owner"]

    sale_price = fields.Float(
        "Sale Price",
        default=1.0,
        digits="Product Price",
        help="Price at which the product is sold to customers.",
    )
    attribute_line_ids = fields.One2many(
        "purchase.attribute.line", "purchase_line_id", "Product Attributes", copy=False
    )
    ean13 = fields.Char("EAN3")
    model = fields.Char("Model")
    brand = fields.Char("Brand")
    id_product = fields.Char("ID. Product")

    lot_ids = fields.One2many("stock.production.lot", "purchase_line_id", "Lot_ids")
    webcam_image_ids = fields.One2many(
        "purchase.line.image", "purchase_line_id", "Images"
    )
    lot_qty = fields.Float(
        string="Serial quantity",
        digits="Product Unit of Measure",
        required=True,
        default=1.0,
    )

    # To do with product multi image
    multi_image_ids = fields.Many2many("ir.attachment", string="Images")

    cc_type = fields.Selection(related="order_id.cc_type", store=True)
    police = fields.Boolean(related="product_id.police", store=True)
    limit_date = fields.Date("Limit date")
    police_date = fields.Date("Police date")
    purchase_price_15 = fields.Float(
        "Purchase price at 15 days", related="product_id.purchase_price_15"
    )
    purchase_price_30 = fields.Float(
        "Purchase price at 30 days", related="product_id.purchase_price_30"
    )
    purchase_price_60 = fields.Float(
        "Purchase price at 60 days", related="product_id.purchase_price_60"
    )

    renew_commission = fields.Float("Renew commission")
    renew_price = fields.Float("Renew price", compute='_compute_renew_price')
    renew_price_untaxed = fields.Float("Renew price", compute='_compute_renew_price')

    product_dys_ids = fields.Many2many(
        string="Possible Product dysfuncionslities",
        comodel_name="dysfuncionality",
        compute="_compute_product_dysfuncionality",
    )

    dysfuncionality_ids = fields.Many2many(
        "dysfuncionality",
        "purchase_disfuncionality_rel",
        "line_id",
        "dys_id",
        "Dysfuncionalities",
    )

    product_accessory_ids = fields.Many2many(
        string="Possible Product dysfuncionslities",
        comodel_name="accessory",
        compute="_compute_product_accessory",
        store=False,
    )
    accessory_ids = fields.Many2many(
        "accessory",
        "purchase_accessory_rel",
        "line_id",
        "acc_id_id",
        "Accessories",
    )

    product_state = fields.Selection(
        [
            ("n", "Brand New"),
            ("a", "Perfect State"),
            ("b", "Good State"),
            ("c", "Used"),
        ],
        "Product State",
        required=True,
        default="b",
    )
    dys_discount = fields.Float("Dysfuncionality Discount (%)")
    discounted_price = fields.Float("Discounted Price")
    dys_note = fields.Text("Dysfuncionality Note")
    take_image = fields.Binary("Add Image")

    # jewelry fields
    jew_weight = fields.Float("Weight")
    jew_metal = fields.Char("Metal or material")
    jew_grabation = fields.Char("Grabations")
    jew_weight2 = fields.Float("Stone Weight")

    jewelry = fields.Boolean("Jewelry", related="product_id.jewelry")

    @api.depends("product_id")
    def _compute_product_dysfuncionality(self):
        for line in self:
            line.product_dys_ids = line.product_id.dysfuncionality_ids

    @api.depends("price_unit", "renew_commission")
    def _compute_renew_price(self):
        for line in self:
            renew_price = line.price_unit * (1 + (line.renew_commission / 100))
            line.renew_price = renew_price
            com_amount = renew_price - line.price_unit
            com_tax = com_amount - (com_amount / 1.21)
            line.renew_price_untaxed = renew_price - com_tax

    @api.depends("product_id")
    def _compute_product_accessory(self):
        for line in self:
            line.product_accessory_ids = line.product_id.accessory_ids

    @api.constrains("sale_price", "price_unit")
    def _check_prices(self):
        """ Program code must be unique """
        for line in self:
            if line.sale_price < line.price_unit:
                raise ValidationError(_("Sale price must be greater than cost price"))

    @api.onchange("dysfuncionality_ids")
    def onchange_warning_dysfuncionality_ids(self):
        blocking_dys = self.dysfuncionality_ids.filtered("block_purchase")
        res = {}
        if blocking_dys:
            dys_names = ", ".join(blocking_dys.mapped("name"))
            msg = _(
                "Product %s has "
                "this dysfuncionalities that will block the purchase: %s"
            ) % (self.product_id.name, dys_names)
            warning = {"title": _("Blocked by dysfuncionalitys"), "message": msg}
            res["warning"] = warning

        # dys_discounts = self.dysfuncionality_ids.mapped('discount')
        # dys_discount = sum(dys_discounts)

        # acc_discount = 0
        # mandatory_acess = self.product_id.accessory_ids.filtered('mandatory')
        # if mandatory_acess:
        #     diff_access = mandatory_acess - \
        #         self.accessory_ids.filtered('mandatory')
        #     if diff_access:
        #         acc_discounts = diff_access.mapped('discount')
        #         acc_discount = sum(acc_discounts)
        # total_discount = dys_discount + acc_discount
        # self.dys_discount = total_discount

        # discounted_price = 0.0
        # if total_discount < 100.0:
        #     discounted_price = self.price_unit * (1 - (dys_discount / 100.0))
        # self.discounted_price = discounted_price
        return res

    @api.onchange("accessory_ids", "dysfuncionality_ids", "price_unit")
    def onchange_accessory_dys_discounts_ids(self):
        dys_discounts = self.dysfuncionality_ids.mapped("discount")
        dys_discount = sum(dys_discounts)

        acc_discount = 0
        mandatory_acess = self.product_id.accessory_ids.filtered("mandatory")
        if mandatory_acess:
            diff_access_ids = set(mandatory_acess.ids) - set(
                self.accessory_ids.filtered("mandatory").ids
            )

            if diff_access_ids:
                diff_access = self.env["accessory"].browse(diff_access_ids)
                acc_discounts = diff_access.mapped("discount")
                acc_discount = sum(acc_discounts)
        total_discount = dys_discount + acc_discount
        self.dys_discount = total_discount

        discounted_price = 0.0
        if total_discount < 100.0:
            discounted_price = self.price_unit * (1 - (dys_discount / 100.0))
        self.discounted_price = discounted_price

    @api.onchange("product_id")
    def onchange_product_id(self):
        """
        Preload attributes
        """
        res = super().onchange_product_id()
        # dis_ids = []
        if self.product_id:
            attributes = self.product_id.product_tmpl_id.attribute_line_ids.mapped(
                "attribute_id"
            )
            if attributes:
                att_values = []
                for att in attributes:
                    vals = {"attribute_id": att.id}
                    att_values.append((6, 0, []))
                    att_values.append((0, 0, vals))
                self.attribute_line_ids = att_values

            # avg_cost = self.product_id.get_purchase_price_days_ago(15)
            # self.price_unit = avg_cost
            today = datetime.today()
            if self.product_id.police:
                self.police_date = today + timedelta(days=self.product_id.police_days)

            if self.order_id and self.order_id.cc_type == "recoverable_sale":
                self.limit_date = today + timedelta(days=30)
        return res

    def _prepare_stock_moves(self, picking):
        """
        Propagate lot quantity to the related stock move.
        """
        res = super()._prepare_stock_moves(picking)
        if res and self.lot_qty:
            res[0]["product_uom_qty"] = self.lot_qty
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("multi_image_ids"):
            res.add_images()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("multi_image_ids"):
            self.add_images()
        return res

    def add_images(self):
        for pol in self:
            pol.image_ids.unlink()
            for att in pol.multi_image_ids:
                vals = {
                    "name": att.name,
                    "storage": "filestore",
                    "attachment_id": att.id,
                    "owner_id": pol.id,
                    "owner_model": "purchase.order.line",
                }
                self.env["base_multi_image.image"].create(vals)

    def copy_image_to_lots(self):
        for pol in self:
            if pol.lot_ids and pol.multi_image_ids:
                for lot in pol.lot_ids:
                    lot.image_ids.unlink()
                    lot.multi_image_ids = [
                        (6, 0, [att.id for att in pol.multi_image_ids])
                    ]

    def prepare_lot_vals(self):
        self.ensure_one()
        attribute_line_ids = []
        for att in self.attribute_line_ids:
            values = {
                "attribute_id": att.attribute_id.id,
                "value_ids": [(6, 0, [x.id for x in att.value_ids])],
            }
            attribute_line_ids.append((0, 0, values))
        list_price = self.sale_price
        standard_price = self.price_unit
        if self.lot_qty:
            list_price = list_price / self.lot_qty
            standard_price = standard_price / self.lot_qty
        res = {
            "list_price": list_price,
            "standard_price": standard_price,
            "ean13": self.ean13,
            "model": self.model,
            "brand": self.brand,
            "id_product": self.id_product,
            "attribute_line_ids": attribute_line_ids,
            "dysfuncionality_ids": self.dysfuncionality_ids,
            "accessory_ids": self.accessory_ids,
            "purchase_line_id": self.id,
            "note": self.name,
            "police_date": self.police_date,
            "limit_date": self.limit_date,
            "renew_commission": self.renew_commission,
            "lot_state": "police",
            "product_state": self.product_state,
            "dys_note": self.dys_note,
            "jew_weight": self.jew_weight,
            "jew_metal": self.jew_metal,
            "jew_grabation": self.jew_grabation,
            "jew_weight2": self.jew_weight2,
        }
        return res

    def check_constraints(self):
        self.ensure_one()
        blocking_dys = self.dysfuncionality_ids.filtered("block_purchase")
        if blocking_dys:
            dys_names = ", ".join(blocking_dys.mapped("name"))
            raise UserError(
                _(
                    "Can not confirm order because product %s has "
                    "this dysfuncionalities: %s"
                )
                % (self.product_id.name, dys_names)
            )

        # mandatory_acess = self.product_id.accessory_ids.filtered('mandatory')
        # # if mandatory_acess and self.accessory_ids not in mandatory_acess:
        # if mandatory_acess:
        #     diff_access = mandatory_acess - \
        #         self.accessory_ids.filtered('mandatory')
        #     if diff_access:
        #         acc_names = ','.join(diff_access.mapped('name'))
        #         raise UserError(
        #             _("Can not confirm order because product %s requires "
        #             "next accesories: %s") %
        #             (self.product_id.name, acc_names))


class PurchaseAttributeLine(models.Model):
    _name = "purchase.attribute.line"
    _rec_name = "attribute_id"
    _description = "Purchase Attribute Line"
    _order = "attribute_id, id"

    active = fields.Boolean(default=True)
    purchase_line_id = fields.Many2one(
        "purchase.order.line", string="Purchase", required=True, index=True
    )
    attribute_id = fields.Many2one(
        "product.attribute",
        string="Attribute",
        ondelete="restrict",
        required=True,
        index=True,
    )
    value_ids = fields.Many2many(
        "product.attribute.value",
        string="Values",
        domain="[('attribute_id', '=', attribute_id)]",
        relation="product_attribute_value_purchase_attribute_line_rel",
        ondelete="restrict",
    )


class PurchaseLineImagee(models.Model):
    _name = "purchase.line.image"

    purchase_line_id = fields.Many2one(
        "purchase.order.line", string="Purchase", required=True, index=True
    )
    image = fields.Binary("Add Image")
