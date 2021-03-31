from odoo import _, api, fields, models
from odoo.exceptions import UserError


LOT_STATES = [
    ('police', 'Police'),
    ('recoverable', 'Recoverable'),
    ('for_sale', 'For Sale'),
    ('sold', 'Sold'),
]

class ChangeLotStateWzd(models.TransientModel):
    _name = "change.lot.state.wzd"

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        lots = self.env["stock.production.lot"].browse(
            self._context.get("active_ids", [])
        )
        if lots:
            res["lot_state_orig"] = lots[0].lot_state
        return res

    lot_state_orig = fields.Selection(
        LOT_STATES, string="From State", readonly=True)
    lot_state_dest = fields.Selection(
        LOT_STATES, string="Change to", readonly=False, required=True)
    
    def confirm(self):
        lots = self.env["stock.production.lot"].browse(
            self._context.get("active_ids", [])
        )
        if lots:
            lots.lot_state = self.lot_state_dest

            orig = self.lot_state_orig
            dest = self.lot_state_dest
            msg = _("Manually lot changed state from %s to %s") % (orig, dest)
            for lot in lots:
                lot.message_post(body=msg)


