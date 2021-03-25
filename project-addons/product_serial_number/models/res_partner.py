# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression



class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        OVERWRITED
        EL DE ODOO POR DWL NO PARECE ESTAR FUNCIONANDO BIEN
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|', ('name', operator, name), ('vat', operator, name), ('email', operator, name), (('ref', operator, name))]
        partner_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(partner_ids))

