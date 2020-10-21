
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RecoverableSaleWzd(models.TransientModel):
    _name = "recoverable.sale.wzd"

    product_id = fields.Many2one('product.product', 'Product', required=True)
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', required=True)

    def confirm(self):
        vals = {
            'order_id': self._context.get('active_id'),
            'product_id': self.product_id.id,
            'lot_id': self.lot_id.id,
            'price_unit': self.lot_id.list_price
        }
        line = self.env['sale.order.line'].new(vals)
        line._onchange_product_id_set_lot_domain()
        line._onchange_lot_id()
        line.product_id_change()
        vals = line._convert_to_write(line._cache)
        line = self.env['sale.order.line'].create(vals)
        line.lot_id = self.lot_id.id
        return
