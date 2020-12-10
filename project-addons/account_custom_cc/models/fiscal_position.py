# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountFiscalPositionTemplate(models.Model):
    _name = "account.fiscal.position.template"
    _inherit = "account.fiscal.position.template"

    rebu = fields.Boolean("REBU")


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    rebu = fields.Boolean("REBU")
