# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    # @api.constrains('operating_unit_id')
    # def _check_pos_order_operating_unit(self):
    #     for rec in self:
    #         orders = self.sudo().env['pos.order'].search(
    #             [('crm_team_id', '=', rec.id),
    #              ('operating_unit_id', '!=', rec.operating_unit_id.id)])
    #         if orders:
    #             raise ValidationError(_('Configuration error. It is not '
    #                                     'possible to change this '
    #                                     'team. There are pos orders '
    #                                     'referencing it in other operating '
    #                                     'units'))
