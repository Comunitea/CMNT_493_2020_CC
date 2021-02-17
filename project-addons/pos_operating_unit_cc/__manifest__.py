# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Pos Operating Unit CC",
    "version": "13.0.1.0.0",
    "summary": "An operating unit (OU) is an organizational entity part of a "
    "company",
    "author": "Comunitea, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Sales Management",
     "depends": [
        "point_of_sale", 
        "pos_sale",
        "account_operating_unit", 
        "sales_team_operating_unit",
    ],
    "data": [
        "security/pos_security.xml",
        "views/pos_view.xml",
    ],
    "installable": True,
}
