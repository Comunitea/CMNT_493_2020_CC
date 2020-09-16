# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class ProductTemoplate(models.Model):

    _inherit = 'product.template'

    serial_mgmt = fields.Boolean('Manage by serial number', default=True)
    auto_create_lot = fields.Boolean(default=True)
    # tracking = fields.Selection(default='serial')

    @api.model
    def default_get(self, default_fields):
        """
        Get the payment fields filled when opening from purchase order
        """
        res = super().default_get(default_fields)
        res.update({
            'tracking': 'serial',
        })
        return res

    @api.onchange('serial_mgmt')
    def _onchange_serial_mgmt(self):
        if self.serial_mgmt:
            self.tracking = 'serial'