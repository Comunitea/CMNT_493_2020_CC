# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta



class StockLocation(models.Model):
    _inherit = "stock.location"

    # police = fields.Boolean('Is police location')
    # recoverable_sale = fields.Boolean('Is recoverable sale location')
    # deposit = fields.Boolean('Is deposit location')
    # requisation = fields.Boolean('Is requisation location')
    # safe = fields.Boolean('Is safe location')
    cc_type = fields.Selection(
        [('normal', 'Normal'),
         ('deposit', 'Deposit'),
         ('recoverable_sale', 'Recoverable Sale'),
         ('requisation', 'requisatin'),
         ('safe', 'Safe'),
        ], 'Location type',
         default='normal')