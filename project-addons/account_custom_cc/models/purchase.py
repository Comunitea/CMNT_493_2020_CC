# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    payment_id = fields.Many2one(
        'account.payment', 'Payment', readonly=True)

    def action_instant_payment(self):
        return self.env['account.payment']\
            .with_context(active_ids=self.ids, 
                active_model='purchase.order', active_id=self.id)\
                .action_register_payment()