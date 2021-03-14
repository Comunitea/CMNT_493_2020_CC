# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Pos Custom CC",
    "version": "13.0.0.0.0",
    "category": "Point Of Sale",
    "summary": """
        Point of Sale - Cutomizations Cash COnverters""",
    "author": "Comunitea",
    "website": "https://comunitea.com",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "account_custom_cc", "purchase"],
    "data": [
        "views/assets.xml",
        "wizard/recoverable_sale_wzd.xml",
        "views/pos_order_view.xml",
        "views/purchase_view.xml",
    ],
    "qweb": [
        "static/src/xml/pos_custom_cc.xml",
    ],
}
