# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta



class SaleOrder(models.Model):

    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(required=True)

    # Sobrescrita, bloquear lotes no vendibles
    @api.onchange("product_id")
    def _onchange_product_id_set_lot_domain(self):
        """
        OVERWRITED
        Allow only salable lots
        """
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env["stock.quant"].read_group(
                [
                    ("product_id", "=", self.product_id.id),
                    ("location_id", "child_of", location.id),
                    ("quantity", ">", 0),
                    ("lot_id", "!=", False),
                    ("lot_id.salable", "!=", False),
                ],
                ["lot_id"],
                "lot_id",
            )
            available_lot_ids = [quant["lot_id"][0] for quant in quants]
        self.lot_id = False
        return {"domain": {"lot_id": [("id", "in", available_lot_ids)]}}

    # Price unit from lot
    def _get_display_price(self, product):
        res = super()._get_display_price(product)
        if self.lot_id:
            res = list_price
        return res
    
    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        if self.lot_id:
            self.price_unit = self.lot_id.list_price