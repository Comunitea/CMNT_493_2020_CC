# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    user_code = fields.Char('User Code')