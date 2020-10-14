# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _



class LocationInfo(models.Model):
    _name = "location.info"

    name = fields.Char('name')
