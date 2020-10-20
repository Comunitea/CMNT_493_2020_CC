# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AccountMove(models.Model):
    _inherit = "account.move"

    def _move_autocomplete_invoice_lines_values(self):
        import ipdb; ipdb.set_trace()
        res = super()._move_autocomplete_invoice_lines_values()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        # compute='_compute_prod_lot',
        readonly=False,
        string="Lot",
    )

    invoice_type = fields.Selection(
        related='move_id.type', string="Invoice Type",
        store=True, readonly=True)


    # def _compute_prod_lot(self):
    #     for line in self:
    #         line.lot_id = line.mapped('move_line_ids.move_line_ids.lot_id')