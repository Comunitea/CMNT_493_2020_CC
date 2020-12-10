# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_fp_vals(self, company, position):
        res = super()._get_fp_vals(company, position)
        res["rebu"] = position.rebu
        return res
