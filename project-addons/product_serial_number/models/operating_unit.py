# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class OperatingUnit(models.Model):

    _inherit = "operating.unit"

    lot_seq = fields.Many2one("ir.sequence", "Auto Lot sequence")
    store_code = fields.Char("Store code")
