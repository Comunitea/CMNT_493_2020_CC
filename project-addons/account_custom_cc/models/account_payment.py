# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.model
    def default_get(self, default_fields):
        """
        Get the payment fields filled when opening from purchase order
        """
        res = super().default_get(default_fields)
        active_ids = self._context.get('active_ids') \
            or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'purchase.order':
            return res
        
        purchase = self.env['purchase.order'].browse(active_ids[0])
        res.update({
            'amount': purchase.amount_total,
            'payment_type': 'outbound',
            'partner_id': purchase.partner_id.commercial_partner_id.id,
            'communication': purchase.partner_ref or '',
            'partner_type': 'supplier',
            'state': 'draft',
            'currency_id': 1,
            'payment_difference_handling': 'open',
            'writeoff_label': 'Write-Off',
            'payment_date': fields.Datetime.now()
        })
        return res
    
    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        """
        Return purchase amount total, default_get is not enought because
        _onchange_currency that overwrites amount
        """
        res = super()._compute_payment_amount(
            invoices, currency, journal, date)
        active_ids = self._context.get('active_ids') \
            or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'purchase.order':
            return res
        purchase = self.env['purchase.order'].browse(active_ids[0])
        if purchase:
            res = purchase.amount_total
        return res
        
    def _prepare_payment_moves(self):
        """
        Cambio la cuenta contable de los apuntes, cuando venga el pago desde
        el pedido de compra, buscando el movimiento cuyop debito>0 y poniendo
        la cuenta de gastos del producto
        """
        res = super()._prepare_payment_moves()

        active_ids = self._context.get('active_ids') \
            or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'purchase.order':
            return res

        purchase = self.env['purchase.order'].browse(active_ids[0])
        product = purchase.order_line[0].product_id
        new_account = False
        if product.property_account_expense_id:
            new_account = product.property_account_expense_id
        else:
            new_account = product.categ_id.property_account_expense_categ_id
        for dic in res:
            for line in dic.get('line_ids'):
                dic_line = line[2]
                if dic_line.get('debit') > 0 and new_account:
                    dic_line['account_id'] = new_account.id
                    break;
        return res

    def post(self):
        """
        Link purchase order and payment
        """
        res = super().post()
        active_ids = self._context.get('active_ids') \
            or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'purchase.order':
            return res

        purchase = self.env['purchase.order'].browse(active_ids[0])
        purchase.payment_id = self.id