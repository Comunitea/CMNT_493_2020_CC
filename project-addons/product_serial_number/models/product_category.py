# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"

    jewelry = fields.Boolean("Jewelry")
    is_categ_jewelry = fields.Boolean(
        "Is Jewelry Categ", 
        compute="_compute_is_categ_jewelry", store=True)

    
    @api.depends("jewelry", "parent_id")
    def _compute_is_categ_jewelry(self):
        for cat in self:
            if cat.jewelry or (cat.parent_id and cat.parent_id.is_categ_jewelry):
                cat.is_categ_jewelry = True
            else:
                cat.is_categ_jewelry = False