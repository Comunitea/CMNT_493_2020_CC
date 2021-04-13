# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    contract_text = fields.Text('Contract Text')
    legal_text = fields.Text('Legal Text')
    recoverable_text = fields.Text('Recoverable Text')
    recoverable_text2 = fields.Text('Recoverable Text 2')
