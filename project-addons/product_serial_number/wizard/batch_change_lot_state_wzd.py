from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BatchChangeLotStateWzd(models.TransientModel):
    _name = "batch.change.lot.state.wzd"

    date_start = fields.Date('From', default=fields.Date.today, required=True)
    date_end = fields.Date('To', default=fields.Date.today, required=True)
    operation = fields.Selection([
        ('police_to_sale', 'Police to Sale'),
        ('jewelry_to_sale', 'Police (Jewerly) to Sale'),
        ('police_to_recoverable', 'Police (Recoverable) to Recoverable'),
        ('jewelry_to_recoverable', 'Police (Jewerly Recoverable) to Recoverable'),
        ('recoverable_to_sale', 'Recoverable to Sale')],
        'Operation', required=True)

 
    def confirm(self):
        domain_dates = [
            ('create_date', '>=', self.date_start),
            ('create_date', '<=', self.date_end)
        ]
        lots = False
        if self.operation == 'police_to_sale':
            domain = domain_dates + [
                ('cc_type', '!=', 'recoverable_sale'), 
                ('lot_state', '=', 'police'), 
                ('jewelry', '=', False)
            ]
            lots = self.env["stock.production.lot"].search(domain)
            if not lots:
                raise ValidationError(_('No lots founded for Police to sale'))
            lots.lot_state = 'for_sale'
            msg = _("Lot changed state: Police to sale")
            for lot in lots:
                lot.message_post(body=msg)

        elif self.operation == 'jewelry_to_sale':
            domain = domain_dates + [
                ('cc_type', '!=', 'recoverable_sale'),
                ('lot_state', '=', 'police'), 
                ('jewelry', '=', True)]
            lots = self.env["stock.production.lot"].search(domain)
            if not lots:
                raise ValidationError(_('No lots founded for Jewerly to Sale'))
            lots.lot_state = 'for_sale'
            msg = _("Lot changed state: Jewerly to Sale")
            for lot in lots:
                lot.message_post(body=msg)
        
        elif self.operation == 'police_to_recoverable':
            domain = domain_dates + [
                ('cc_type', '=', 'recoverable_sale'),
                ('lot_state', '=', 'police'), 
                ('jewelry', '=', False)]
            lots = self.env["stock.production.lot"].search(domain)
            if not lots:
                raise ValidationError(_('No lots founded for Police (Recoverable) to Recoverable'))
            lots.lot_state = 'recoverable'
            msg = _("Lot changed state: Police (Recoverable) to Recoverable")
            for lot in lots:
                lot.message_post(body=msg)
        
        elif self.operation == 'jewelry_to_recoverable':
            domain = domain_dates + [
                ('cc_type', '=', 'recoverable_sale'),
                ('lot_state', '=', 'police'), 
                ('jewelry', '=', True)]
            lots = self.env["stock.production.lot"].search(domain)
            if not lots:
                raise ValidationError(_('No lots founded for Jewerly (Recoverable) to Recoverable'))
            lots.lot_state = 'recoverable'
            msg = _("Lot changed state: Jewerly (Recoverable) to Recoverable")
            for lot in lots:
                lot.message_post(body=msg)
        
        elif self.operation == 'recoverable_to_sale':
            domain = domain_dates + [('lot_state', '=', 'recoverable')] 
            lots = self.env["stock.production.lot"].search(domain)
            if not lots:
                raise ValidationError(_('No lots founded for Recoverable to Sale'))
            lots.lot_state = 'for_sale'
            msg = _("Lot changed state: Jewerly (Recoverable) to Recoverable")
            for lot in lots:
                lot.message_post(body=msg)

        elif not lots:
            raise ValidationError(_('No lots founded'))