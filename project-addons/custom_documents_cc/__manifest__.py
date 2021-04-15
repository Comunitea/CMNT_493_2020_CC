# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom Documents CC",
    "version": "13.0.0.0.1",
    "category": "Custom",
    "author": "Coumnitea",
    "contributors": [
        "Javier Colmenero <javier@comunitea.com>",
    ],
    "website": "http://www.comunitea.com",
    "support": "info@comunitea.com",
    "license": "AGPL-3",
    "depends": [
        "account",
        "sale",
        "purchase",
        "web",
        "sale_stock",
        "stock",
        "product_serial_number",
    ],
    "data": [
        "views/res_company_view.xml",
        "data/ir_config_parameter.xml",
        "views/purchase_view.xml",
        "views/product_attribute_view.xml",
        "views/report_templates.xml",
        "views/report_purchase_order.xml",
        "views/report_police.xml",
        "views/report_police_jewelry.xml",
        "views/report_lot_label_purchase.xml",
        "wizard/police_report_wzd.xml",
    ],
    "images": [
        "/static/description/icon.png",
    ],
    "installable": True,
    "application": False,
}
