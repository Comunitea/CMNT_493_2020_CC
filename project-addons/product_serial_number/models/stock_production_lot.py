# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class ProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    standard_price = fields.Float('Cost', digits='Product Price')
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")
    attribute_line_ids = fields.One2many(
        'lot.attribute.line', 'lot_id', 
        'Product Attributes', copy=True)
    
    ean13 = fields.Char('EAN3')
    model = fields.Char('Model')
    brand = fields.Char('Brand')
    id_product = fields.Char('ID. Product')


class LotAttributeLine(models.Model):
    """Attributes available on product.template with their selected values in a m2m.
    Used as a configuration model to generate the appropriate product.template.attribute.value"""

    _name = "lot.attribute.line"
    _rec_name = 'attribute_id'
    _description = 'Lot Attribute Line'
    _order = 'attribute_id, id'

    active = fields.Boolean(default=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string="Lot", ondelete='cascade', 
        required=True, index=True)
    attribute_id = fields.Many2one(
        'product.attribute', string="Attribute", ondelete='restrict',
        required=True, index=True)
    value_ids = fields.Many2many(
        'product.attribute.value', string="Values", domain="[('attribute_id', '=', attribute_id)]",
        relation='product_attribute_value_lot_attribute_line_rel',
        ondelete='restrict')
    # product_template_value_ids = fields.One2many(
    #     'product.template.attribute.value', 'attribute_line_id',
    #     string="Product Attribute Values")