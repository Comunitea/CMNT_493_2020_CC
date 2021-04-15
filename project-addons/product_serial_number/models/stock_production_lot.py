# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductionLot(models.Model):

    _name = "stock.production.lot"
    _inherit = [_name, "base_multi_image.owner"]

    _order = "create_date desc"

    standard_price = fields.Float("Cost", digits="Product Price")
    list_price = fields.Float(
        "Sales Price",
        default=1.0,
        digits="Product Price",
        help="Price at which the product is sold to customers.",
    )
    attribute_line_ids = fields.One2many(
        "lot.attribute.line", "lot_id", "Product Attributes", copy=True
    )

    ean13 = fields.Char("EAN3")
    model = fields.Char("Model")
    brand = fields.Char("Brand")
    id_product = fields.Char("Nº Serie")
    ubic_acc = fields.Char("Accesory location")
    label_info_str = fields.Char("Label info", compute="_compute_label_info")

    purchase_line_id = fields.Many2one("purchase.order.line", "Purchase line")
    cc_type = fields.Selection(related="purchase_line_id.cc_type", store=True)

    # To do with product multi image
    multi_image_ids = fields.Many2many("ir.attachment", string="Images")
    police_date = fields.Date("Police date")
    limit_date = fields.Date("Limit date")

    salable = fields.Boolean("Salable", compute="_compute_salable", store=True)

    location_info_id = fields.Many2one("location.info", "Main Loacation")
    location_info_ids = fields.Many2many(
        "location.info",
        "stock_location_loc_info_rel",
        "loc_id",
        "info_id",
        string="Alternative Loacation",
    )

    lot_location_id = fields.Many2one(
        "stock.location", compute="_compute_location", store=True
    )
    renew_commission = fields.Float("Renew commission")
    recovered = fields.Boolean("Product recovered")
    num_renew = fields.Integer("Nº renews")

    lot_state = fields.Selection(
        [
            ("police", "Police"),
            ("recoverable", "Recoverable"),
            ("for_sale", "For Sale"),
            ("sold", "Sold"),
        ],
        string="Lot State",
        readonly=False,
    )
    jewelry = fields.Boolean("Jewelry", related="product_id.jewelry", store=True)

    product_dys_ids = fields.Many2many(
        string="Possible Product dysfuncionslities",
        comodel_name="dysfuncionality",
        compute="_compute_product_dysfuncionality",
    )

    dysfuncionality_ids = fields.Many2many(
        "dysfuncionality",
        "lot_disfuncionality_rel",
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
        "lot_accessory_rel",
        "line_id",
        "acc_id_id",
        "Disfuncionality",
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

    dys_note = fields.Text("Dysfuncionality Note")

    jew_weight = fields.Float("Weight")
    jew_metal = fields.Char("Metal or material")
    jew_grabation = fields.Char("Grabations")
    jew_weight2 = fields.Char("Stone Weight")

    def _compute_label_info(self):
        for lot in self:
            info_str = ""
            if lot.purchase_line_id:
                po = lot.purchase_line_id.order_id
                if po.operating_unit_id:
                    info_str += po.operating_unit_id.store_code
                if po.user_id:
                    info_str += " (" + po.user_id.user_code + ")"
                if po.date_order:
                    date_order_str = po.date_order.strftime('%d%m%y')
                    blacksmith_map = {
                        '0': 'B',
                        '1': 'L',
                        '2': 'A',
                        '3': 'C',
                        '4': 'K',
                        '5': 'S',
                        '6': 'M',
                        '7': 'I',
                        '8': 'T',
                        '9': 'H',
                    }
                    blacksmit_str = ""
                    for ch in date_order_str:
                        if ch in blacksmith_map:
                            blacksmit_str += blacksmith_map[ch]
                    info_str += " (" + blacksmit_str + ")"

            lot.label_info_str = info_str

    @api.depends("product_id")
    def _compute_product_dysfuncionality(self):
        for lot in self:
            lot.product_dys_ids = lot.product_id.dysfuncionality_ids

    @api.depends("product_id")
    def _compute_product_accessory(self):
        for lot in self:
            lot.product_accessory_ids = lot.product_id.accessory_ids

    @api.depends("quant_ids.location_id")
    def _compute_location(self):
        for lot in self:
            if lot.quant_ids.filtered(lambda x: x.quantity > 0):
                lot.lot_location_id = lot.quant_ids.filtered(lambda x: x.quantity > 0)[
                    0
                ].location_id.id

    # @api.depends("police_date", "limit_date", "lot_location_id")
    @api.depends("lot_state")
    def _compute_salable(self):
        for lot in self:
            # res = True
            # if lot.police_date and lot.police_date > fields.Date.today():
            #     res = False
            # elif lot.limit_date and lot.limit_date > fields.Date.today():
            #     res = False
            # elif lot.lot_location_id:
            #     location = lot.lot_location_id.get_warehouse().lot_stock_id
            #     domain = [
            #         ("id", "=", lot.lot_location_id.id),
            #         ("id", "child_of", location.id),
            #     ]
            #     is_stock_location = self.env["stock.location"].search(domain)
            #     if not is_stock_location:
            #         res = False
            # lot.salable = res
            lot.salable = True if lot.lot_state == "for_sale" else False

    @api.model
    def create(self, vals):
        """
        If operating unit in context get name from lot sequece field
        """
        # Naming lot
        if self._context.get("ou_id"):
            ou = self.env["operating.unit"].browse(self._context.get("ou_id"))
            if ou.lot_seq:
                vals["name"] = ou.lot_seq.next_by_id()
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
        for lot in self:
            lot.image_ids.unlink()
            for att in lot.multi_image_ids:
                vals = {
                    "name": att.name,
                    "storage": "filestore",
                    "attachment_id": att.id,
                    "owner_id": lot.id,
                    "owner_model": "stock.production.lot",
                }
                self.env["base_multi_image.image"].create(vals)

    def _cron_compute_salable_lots(self):
        """
        Desactivado, NO NECESARIO
        """
        domain = []
        lots = self.env["stock.production.lot"].search(domain)
        lots._compute_salable()


class LotAttributeLine(models.Model):
    """Attributes available on product.template with their selected values in a m2m.
    Used as a configuration model to generate the appropriate
    product.template.attribute.value"""

    _name = "lot.attribute.line"
    _rec_name = "attribute_id"
    _description = "Lot Attribute Line"
    _order = "attribute_id, id"

    active = fields.Boolean(default=True)
    lot_id = fields.Many2one(
        "stock.production.lot",
        string="Lot",
        ondelete="cascade",
        required=True,
        index=True,
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
        relation="product_attribute_value_lot_attribute_line_rel",
        ondelete="restrict",
    )
