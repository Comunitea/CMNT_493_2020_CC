# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, _, fields
from odoo.exceptions import UserError
from datetime import datetime


class ReportPolicejewelryParser(models.AbstractModel):
    """
    """
    _name = 'report.custom_documents_cc.report_police_jewelry'

    @api.model
    def _get_report_values(self, docids, data=None):
        lot_ids = data.get('lot_ids')
        if not lot_ids:
            lot_ids = docids
        lots = self.env['stock.production.lot'].browse(lot_ids)

        grouped_lots = {}
        for l in lots:
            po = l.purchase_line_id.order_id
            if po not in grouped_lots:
                grouped_lots[po] = self.env['stock.production.lot']
            grouped_lots[po] += l

        purchases = lots.mapped('purchase_line_id.order_id')
        ordered_purchases = purchases.sorted(lambda p: p.date_order)
       
        user = self.env['res.users'].browse(self._uid)
        footer_data = {
            'create_date': datetime.now().strftime("%d/%m/%Y %H/%M"),
            'user': user.user_code,
        }
        
        date_start =  datetime.now().strftime("%d-%m-%Y")
        if data.get('date_start'):
            date_start = data['date_start']
        date_end =  datetime.now().strftime("%d-%m-%Y")
        if data.get('date_end'):
            date_end= data['date_end']

        return {
            'doc_ids': lots.ids,
            'data': data,
            'docs': lots,
            "dt_start": date_start,
            "dt_end": date_end,
            'user_company': user.company_id,
            'footer_data': footer_data,
            'ordered_purchases': ordered_purchases,
            'grouped_lots': grouped_lots,
        }
