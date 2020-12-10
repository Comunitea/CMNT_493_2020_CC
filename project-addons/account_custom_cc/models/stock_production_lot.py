# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductionLot(models.Model):

    _inherit = "stock.production.lot"

    rebu = fields.Boolean("REBU", readonly=True)
    itp_1_3 = fields.Float("itp 1/3", readonly=True)
