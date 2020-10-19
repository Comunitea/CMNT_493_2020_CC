
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TransferLotWzd(models.TransientModel):
    _name = "transfer.lot.wzd"

    location_id = fields.Many2one(
        'stock.location', 'Origin location', required=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Dest location', required=True)

    def confirm(self):
        lots =  self.env['stock.production.lot'].browse(
            self._context.get('active_ids', []))
        
        wzd_obj = self.env['wiz.stock.move.location']
        vals = {
            'origin_location_id': self.location_id.id,
            'destination_location_id': self.location_dest_id.id,
        }

        domain = [
            ("product_id", "in", lots.mapped('product_id').ids),
            ("location_id", "child_of", self.location_id.id),
            ("quantity", ">", 0),
            ("lot_id", "!=", False),
        ]
        quants = self.env["stock.quant"].search(domain)
        ctx = self._context.copy()
        ctx['active_ids'] = quants.ids
        wzd = wzd_obj.with_context(ctx).create(vals)
        wzd.write({
            'stock_move_location_line_ids': [
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
        })
        return wzd.action_move_location()