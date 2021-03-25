# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class Dysfuncionality(models.Model):

    _name = "dysfuncionality"

    name = fields.Char('Name')
    block_purchase = fields.Boolean('Block Purchase')
    print_in_ticket = fields.Boolean('Print in ticket', default=True)
    discount = fields.Float('Discount')