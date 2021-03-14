from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TransferLotWzd(models.TransientModel):
    _name = "transfer.lot.wzd"

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        lots = self.env["stock.production.lot"].browse(
            self._context.get("active_ids", [])
        )
        location = lots.mapped("lot_location_id")
        if len(location) != 1:
            raise UserError(_("Please, select lots of the same location"))

        res["location_id"] = location.id
        return res

    location_id = fields.Many2one("stock.location", "Origin location", required=True)
    location_dest_id = fields.Many2one("stock.location", "Dest location", required=True)

    def confirm(self):
        lots = self.env["stock.production.lot"].browse(
            self._context.get("active_ids", [])
        )

        wzd_obj = self.env["wiz.stock.move.location"]
        vals = {
            "origin_location_id": self.location_id.id,
            "destination_location_id": self.location_dest_id.id,
        }

        domain = [
            ("product_id", "in", lots.mapped("product_id").ids),
            ("location_id", "child_of", self.location_id.id),
            ("quantity", ">", 0),
            ("lot_id", "in", lots.ids),
        ]
        quants = self.env["stock.quant"].search(domain)
        ctx = self._context.copy()
        ctx["active_ids"] = quants.ids
        wzd = wzd_obj.with_context(ctx).create(vals)
        wzd.write(
            {
                "stock_move_location_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": quant.product_id.id,
                            "move_quantity": quant.quantity,
                            "max_quantity": quant.quantity,
                            "origin_location_id": quant.location_id.id,
                            "destination_location_id": self.location_dest_id.id,
                            "lot_id": quant.lot_id.id,
                            "product_uom_id": quant.product_uom_id.id,
                            "custom": False,
                        },
                    )
                    for quant in quants
                ]
            }
        )
        return wzd.action_move_location()
