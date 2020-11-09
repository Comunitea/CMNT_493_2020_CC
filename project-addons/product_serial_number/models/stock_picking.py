# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """
        Añadir Unidad operacional al contexto para que el método de autogenerar
        lotes, al hacer el create se pase a este la unidad operacional para
        crearlo con la sequencia de la tienda
        """
        ctx = self._context.copy()
        if self.purchase_id and self.purchase_id.operating_unit_id:
            if self.purchase_id.operating_unit_id.lot_seq:
                ctx.update(ou_id=self.purchase_id.operating_unit_id.id)
        return super(StockPicking, self.with_context(ctx)).button_validate()
