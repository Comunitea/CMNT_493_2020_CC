# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'


    def _create_picking(self):
        """
        Automatic create serial numbers using dependency oca module
        """
        res = super()._create_picking()
        pickings = self.picking_ids.filtered(lambda x: x.state == 'assigned')
        for pick in pickings:
            # for move in pick.move_ids_without_package:
            #     move.next_serial = 'Aa1'
            #     move._generate_serial_numbers(
            #         next_serial_count=0)
            pick.button_validate()        
        return True


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    sale_price = fields.Float(
        'Sale Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")
    attribute_line_ids = fields.One2many(
        'purchase.attribute.line', 'purchase_id', 
        'Product Attributes', copy=True)
    ean13 = fields.Char('EAN3')
    model = fields.Char('Model')
    brand = fields.Char('Brand')
    id_product = fields.Char('ID. Product')

    # To do with product multi image
    # image_ids = fields.Many2many('ir.attachment', string='Images')


class PurchaseAttributeLine(models.Model):
    _name = "purchase.attribute.line"
    _rec_name = 'attribute_id'
    _description = 'Purchase Attribute Line'
    _order = 'attribute_id, id'

    active = fields.Boolean(default=True)
    purchase_id = fields.Many2one(
        'purchase.order', string="Purchase", ondelete='cascade', 
        required=True, index=True)
    attribute_id = fields.Many2one(
        'product.attribute', string="Attribute", ondelete='restrict',
        required=True, index=True)
    value_ids = fields.Many2many(
        'product.attribute.value', string="Values",
        domain="[('attribute_id', '=', attribute_id)]",
        relation='product_attribute_value_lot_attribute_line_rel',
        ondelete='restrict')
