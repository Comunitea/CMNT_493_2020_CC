# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class ProductAttribute(models.Model):

    _inherit = 'product.attribute'

    create_variant = fields.Selection(default='no_variant')

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        If attribute field from custom model lot.attribute.line or 
        purchase.attribute.line, limit attributes to the template ones.
        """
        res = super().name_search(
            name, args=args, operator=operator, limit=limit)
        if self._context.get('limit_attributes_product'):
            product_id = self._context.get('limit_attributes_product')
            product = self.env['product.product'].browse(product_id)
            if product.attribute_line_ids:
                attribute_ids = product.product_tmpl_id.\
                    attribute_line_ids.mapped('attribute_id')
                domain = [('id', 'in', attribute_ids.ids)]
                return self.search(domain, limit=limit).name_get()
        return res