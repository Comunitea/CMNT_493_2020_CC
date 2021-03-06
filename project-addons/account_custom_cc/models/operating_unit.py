# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class OperatingUnit(models.Model):

    _inherit = "operating.unit"

    itp_tax_id = fields.Many2one("account.tax", "ITP Tax")
