# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    lot_id = fields.Many2one("stock.production.lot", "Lot", readonly=True)
    rebu = fields.Boolean("REBU")
    purchase_id = fields.Many2one(
        "purchase.order", "Recoverable purchase", readonly=True
    )

    def _order_fields(self, ui_order):
        """
        No fiscal position in pos order, because we have lines with rebu.
        Lines must have the tax already mapped. We do it in the creation of
        the pos.order.line
        """
        res = super()._order_fields(ui_order)
        res["fiscal_position_id"] = False
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    lot_id = fields.Many2one("stock.production.lot", "Lot", readonly=True)
    rebu = fields.Boolean("REBU")
    description = fields.Char("Description")

    def _order_line_fields(self, line, session_id=None):
        """
        Get rebu and lot fields.
        Map rebu fiscal position to get the correct taxes
        """
        res = super()._order_line_fields(line, session_id=session_id)
        res[2]["lot_id"] = line[2]["lot_id"]
        res[2]["rebu"] = line[2]["rebu"]
        if line[2]["rebu"]:
            company_id = self.env["res.users"].browse(self._uid).company_id.id
            ref = "account_custom_cc." + str(company_id) + "_" + "fp_rebu"
            fp_rebu = self.env.ref(ref)
            taxes = self.env["account.tax"]
            for tax in line[2]["tax_ids"]:
                tax_id = tax[2][0]
                taxes |= self.env["account.tax"].browse(tax_id)
            product = self.env["product.product"].browse(line[2]["product_id"])
            rebu_taxes = fp_rebu.map_tax(taxes, product, False)
            if rebu_taxes:
                ids_tax = [r.id for r in rebu_taxes]
                res[2]["tax_ids"] = [[6, False, ids_tax]]

        if "description" in line[2] and line[2]["description"]:
            res[2]["description"] = line[2]["description"]
        return res
