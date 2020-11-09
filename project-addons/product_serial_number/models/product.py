# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    serial_mgmt = fields.Boolean("Manage by serial number", default=True)
    police = fields.Boolean("Police")
    police_days = fields.Integer("Retain days")
    auto_create_lot = fields.Boolean(default=True)
    # tracking = fields.Selection(default='serial')

    @api.model
    def default_get(self, default_fields):
        """
        Get the payment fields filled when opening from purchase order
        """
        res = super().default_get(default_fields)
        res.update(
            {
                "tracking": "serial",
            }
        )
        return res

    @api.onchange("serial_mgmt")
    def _onchange_serial_mgmt(self):
        if self.serial_mgmt:
            self.tracking = "serial"


class ProductProduct(models.Model):

    _inherit = "product.product"

    purchase_price_15 = fields.Float(
        "Purchase price at 15 days", compute="_compute_days_price"
    )
    purchase_price_30 = fields.Float(
        "Purchase price at 30 days", compute="_compute_days_price"
    )
    purchase_price_60 = fields.Float(
        "Purchase price at 60 days", compute="_compute_days_price"
    )

    def get_lines_by_date(self, days_ago):
        self.ensure_one()
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_ago = (datetime.now() - relativedelta(days=days_ago)).strftime("%Y-%m-%d")
        domain = [
            ("product_id", "=", self.id),
            ("order_id.date_order", ">=", date_ago),
            ("order_id.date_order", "<=", current_date),
            ("order_id.state", "in", ["purchase", "done"]),
        ]
        lines = self.env["purchase.order.line"].search(domain)
        return lines

    def get_purchase_price_days_ago(self, days_ago):
        self.ensure_one()
        res = 0
        lines = self.get_lines_by_date(days_ago)
        price_total = 0
        total_lines = len(lines)
        for li in lines:
            price_total += li.price_unit / li.lot_qty if li.lot_qty else 0
        if price_total and total_lines:
            res = price_total / total_lines
        return res

    def _compute_days_price(self):
        for product in self:
            product.purchase_price_15 = product.get_purchase_price_days_ago(15)
            product.purchase_price_30 = product.get_purchase_price_days_ago(30)
            product.purchase_price_60 = product.get_purchase_price_days_ago(60)
