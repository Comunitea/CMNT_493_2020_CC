# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class ProductTemoplate(models.Model):

    _inherit = 'product.template'

    serial_mgmt = fields.Boolean('Manage by serial number', default=True)
    auto_create_lot = fields.Boolean(default=True)

    @api.onchange('serial_mgmt')
    def _onchange_serial_mgmt(self):
        if self.serial_mgmt:
            self.tracking = 'serial'