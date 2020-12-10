# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def _compute_count_pos_orders(self):
        for order in self:
            order.count_pos_orders = len(order.pos_order_ids)

    count_pos_orders = fields.Integer("TpV Orders", compute="_compute_count_pos_orders")
    pos_order_ids = fields.One2many("pos.order", "purchase_id", "TpV Orders")

    def view_pos_orders_button(self):
        self.ensure_one()
        pos_orders = self.pos_order_ids
        action = self.env.ref("point_of_sale.action_pos_pos_form").read()[0]
        if len(pos_orders) > 1:
            action["domain"] = [("id", "in", pos_orders.ids)]
        elif len(pos_orders) == 1:
            form_view_name = "point_of_sale.view_pos_pos_form"
            action["views"] = [(self.env.ref(form_view_name).id, "form")]
            action["res_id"] = pos_orders.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
