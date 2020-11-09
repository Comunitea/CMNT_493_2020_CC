# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# from datetime import datetime

# from dateutil.relativedelta import relativedelta

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    # Redefined to trigger onchange with lot_id
    # price_subtotal = fields.Monetary(compute='_compute_amount')
    # price_tax = fields.Float(compute='_compute_amount')
    # price_total = fields.Monetary(compute='_compute_amount')

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id',
    #              'lot_id')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     Its only added lot_id to triiger and pass the context
    #     """
    #     for line in self:
    #         lot_id = line.lot_id.id
    #         super(SaleOrderLine, line.with_context(serial_lot_id=lot_id)).\
    #             _compute_amount()
    #     # return super()._compute_amount()

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({"lot_id": self.lot_id.id})
        return res
