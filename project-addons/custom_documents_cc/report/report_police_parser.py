# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ReportPolice(models.AbstractModel):
    """
    """
    _name = 'report.custom_documents_cc.report_police'

    @api.model
    def _get_report_values(self, docids, data=None):
        # TODO control viene de compra
        lot_ids = data.get('lot_ids')
        if not lot_ids:
            lot_ids = docids
        lots = self.env['stock.production.lot'].browse(lot_ids)

        grouped_lots = {}
        for l in lots:
            if l.purchase_line_id.order_id not in grouped_lots:
                order = l.purchase_line_id.order_id
                grouped_lots[order] = self.env['stock.production.lot']
            grouped_lots[order] += l

        purchases = lots.mapped('purchase_line_id.order_id')
        ordered_purchases = purchases.sorted(lambda p: p.date_order)
       

        report_data = {lots[0]: lots[0]}
        
        return {
            'doc_ids': lots.ids,
            'data': data,
            'docs': lots,
            'report_data': report_data,
            'ordered_purchases': ordered_purchases,
            'grouped_lots': grouped_lots,
        }
