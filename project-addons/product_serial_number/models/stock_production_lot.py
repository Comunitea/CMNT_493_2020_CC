# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductionLot(models.Model):

    _name = "stock.production.lot"
    _inherit = [_name, "base_multi_image.owner"]

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
    id_product = fields.Char("ID. Product")

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

    @api.depends("quant_ids.location_id")
    def _compute_location(self):
        for lot in self:
            lot.lot_location_id = lot.quant_ids.filtered(
                lambda x: x.quantity > 0
            ).location_id.id

    @api.depends("police_date", "limit_date")
    def _compute_salable(self):
        for lot in self:
            res = True
            if lot.police_date and lot.police_date > fields.Date.today():
                res = False
            lot.salable = res

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
