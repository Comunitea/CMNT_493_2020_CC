# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    to_print = fields.Boolean('To print')
