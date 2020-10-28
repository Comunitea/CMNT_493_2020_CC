# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AccountTax(models.Model):
    _inherit = "account.tax"

    rebu = fields.Boolean('REBU')

    # def _compute_amount(self, base_amount, price_unit, 
    #                     quantity=1.0, product=None, partner=None):
    #     self.ensure_one()
    #     # if self.amount_type == 'code' and not \
    #     #         self._context.get('serial_lot_id'):
    #     #     print('ERROR')
    #         # raise UserError(
    #         #     'The tax {} needs a lot in the context'.format(self.name))
    #     if self._context.get('serial_lot_id'):
    #         lot = self.env['stock.production.lot'].browse(
    #             self._context.get('serial_lot_id'))
    #         base_amount -= (lot.standard_price * quantity)
    #     res = super()._compute_amount(
    #         base_amount, price_unit, quantity, product, partner)
    #     return res

    # def compute_all(self, price_unit, currency=None, quantity=1.0, 
    #                 product=None, partner=None, is_refund=False,
    #                 handle_price_include=True):
    #     if self.amount_type == 'code' and not \
    #             self._context.get('serial_lot_id'):
    #         print('ERROR')
    #         # raise UserError(
    #         #     'The tax {} needs a lot in the context'.format(self.name) )
    #     return super().compute_all(
    #         price_unit, currency, quantity, product, partner,
    #         is_refund=is_refund, handle_price_include=handle_price_include)


class AccountTaxTemplate(models.Model):
    _name = 'account.tax.template'
    _inherit = 'account.tax.template'

    rebu = fields.Boolean('REBU')

    def _get_tax_vals(self, company, tax_template_to_tax):
        self.ensure_one()
        vals = super()._get_tax_vals(company, tax_template_to_tax)
        vals.update({
            'rebu': self.rebu,
        })
        # if self.tax_group_id:
        #     vals['tax_group_id'] = self.tax_group_id.id
        return vals
