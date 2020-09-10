# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def _count_lots(self):
        for order in self:
            order.count_lots = len(order.mapped('order_line.lot_ids'))

    count_lots = fields.Integer('Lots',
                                compute='_count_lots')

    def _create_picking(self):
        """
        Automatic create serial numbers using dependency oca module.
        Copy purchase lot info to the serial numbers created.
        """
        res = super()._create_picking()
        for po in self:
            pickings = po.picking_ids.filtered(lambda x: x.state == 'assigned')
            for pick in pickings:
                # Si no escribo la cantidad hecha no se queda en done el
                # albarán en el button validate
                for move in pick.move_line_ids:
                    move.qty_done = 1
                pick.button_validate()
            
            # Copy serial number info to the line
            for line in po.order_line:
                lot_ids = line.mapped('move_ids.move_line_ids.lot_id')
                if not lot_ids:
                    continue
                attribute_line_ids = []
                for att in line.attribute_line_ids:
                    values = {
                        'attribute_id': att.attribute_id.id,
                        'value_ids': [(6, 0, [x.id for x in att.value_ids])]
                    }
                    attribute_line_ids.append((0, 0, values))
                

                list_price = line.sale_price
                standard_price = line.price_unit
                if line.lot_qty:
                    list_price = list_price / line.lot_qty
                    standard_price = standard_price / line.lot_qty
                

                vals = {
                    'list_price': list_price,
                    'standard_price': standard_price,
                    'ean13': line.ean13,
                    'model': line.model,
                    'brand': line.brand,
                    'id_product': line.id_product,
                    'attribute_line_ids': attribute_line_ids,
                    'purchase_line_id': line.id
                }
                lot_ids.write(vals)
        return res
    
    def view_lots_button(self):
        self.ensure_one()
        lots = self.mapped('order_line.lot_ids')
        action = self.env.ref(
            'stock.action_production_lot_form').read()[0]
        if len(lots) > 1:
            action['domain'] = [('id', 'in', lots.ids)]
        elif len(lots) == 1:
            form_view_name = 'stock.view_production_lot_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = lots.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class PurchaseOrderLine(models.Model):

    _name = 'purchase.order.line'
    _inherit =  [_name, "base_multi_image.owner"]

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

    lot_ids = fields.One2many('stock.production.lot', 'purchase_line_id',
                              'Lot_ids')
    lot_qty = fields.Float(
        string='Serial quantity', digits='Product Unit of Measure')


    # To do with product multi image
    multi_image_ids = fields.Many2many('ir.attachment', string='Images')


    def _prepare_stock_moves(self, picking):
        """
        Propagate lot quantity to the related stock move.
        """
        res = super()._prepare_stock_moves(picking)
        if res and self.lot_qty:
            res[0]['product_uom_qty'] = self.lot_qty
        return res
    
    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('multi_image_ids'):
            res.add_images()
        return res
    
    def write(self, vals):
        res = super().write(vals)
        if vals.get('multi_image_ids'):
            self.add_images()
        return res
    
    def add_images(self):
        for pol in self.filtered('multi_image_ids'):
            pol.image_ids.unlink()
            for att in pol.multi_image_ids:
                vals = {
                    'name': att.name,
                    'storage': 'filestore',
                    'attachment_id': att.id,
                    'owner_id': pol.id,
                    'owner_model':'purchase.order.line'
                }
                self.env['base_multi_image.image'].create(vals)
    
    def copy_image_to_lots(self):
        for pol in self:
            if pol.lot_ids and pol.multi_image_ids:
                for lot in pol.lot_ids:
                    lot.image_ids.unlink()
                    lot.multi_image_ids = [
                        (6,0, [att.id for att in pol.multi_image_ids])]


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
        relation='product_attribute_value_purchase_attribute_line_rel',
        ondelete='restrict')
