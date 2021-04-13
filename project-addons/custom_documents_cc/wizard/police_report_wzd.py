from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PoliceReportWzd(models.TransientModel):
    _name = "police.report.wzd"

    date_start = fields.Date('From', default=fields.Date.today, required=True)
    date_end = fields.Date('To', default=fields.Date.today, required=True)
    num_order = fields.Integer('Nº Order')
    num_order_jewlery = fields.Integer('Nº Order Jewerly')
    num_page = fields.Integer('Nº Page')
    num_page_jewlery = fields.Integer('Nº Page Jewerly')
    jewlery = fields.Boolean('Jewlery')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        icp = self.env['ir.config_parameter']
        num_order = icp.get_param('last.num.order')
        res.update({
            'num_order': int(num_order),
            'num_order_jewlery': 11,
            'num_page': 12,
            'num_page_jewlery': 13,
        })
        return res
 
    def confirm(self):
        domain = [
            ('lot_state', '=', 'police'), 
            ('create_date', '>=', self.date_start),
            ('create_date', '<=', self.date_end),
            ('jewelry', '=', self.jewlery)
        ]
        lots = False
        lots = self.env["stock.production.lot"].search(
            domain, order='create_date')
        if not lots:
            raise ValidationError(_('No lots founded'))
        return self.print_report(lots)
    
    def print_report(self, lots):
        report_name = 'custom_documents_cc.report_police'
        data_dic = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'lot_ids': lots.ids
        }

        icp = self.env['ir.config_parameter']
        new_num_order = self.num_order + 1
        icp.set_param('last.num.order', str(new_num_order))

        # Esto devolverá el report pasando por el parser
        return {
            'type': 'ir.actions.report',
            'report_name': report_name,
            'report_type': 'qweb-pdf',
            'data': data_dic,
        }

